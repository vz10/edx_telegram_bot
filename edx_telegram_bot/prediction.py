# -*- coding: utf-8 -*-

import re
import snowballstemmer
import numpy as np
import sklearn as sk
import scipy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from xmodule.modulestore.django import modulestore
from openedx.core.djangoapps.models.course_details import CourseDetails
from student.models import CourseEnrollment

from models import (TfidMatrixAllCourses, MatrixEdxCoursesId, PredictionForUser,
                    LearningPredictionForUser, EdxTelegramUser, TfidUserVector)


def get_coursed_and_create_matrix():
    results = modulestore().get_courses()
    stemmer = snowballstemmer.stemmer('english')

    results = [course for course in results if
               course.scope_ids.block_type == 'course']

    all_courses = [re.sub('<[^>]*>', '', CourseDetails.fetch_about_attribute(x.id, 'overview')) for x in results]
    map(lambda x: MatrixEdxCoursesId.objects.get_or_create(course_key=x.id, course_index=results.index(x)), results)

    courses_stem = [' '.join(stemmer.stemWords(x.split())) for x in all_courses]
    #TODO remove it when it will be more then one course here
    courses_stem = courses_stem*5
    vect = TfidfVectorizer(stop_words=get_stop_words(), lowercase=True, dtype=np.float32)
    matrix = vect.fit_transform(courses_stem)
    new_matrix = TfidMatrixAllCourses.objects.all().first() or TfidMatrixAllCourses()
    new_matrix.matrix=matrix
    new_matrix.save()


def get_stop_words():
   result = set()
   for line in open('edx-telegram-bot/edx_telegram_bot/stopwords_en.txt', 'r').readlines():
        result.add(line.strip())
   return result


def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx


def get_test_courses(telegram_id):
    telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
    test_courses = LearningPredictionForUser.objects.get_or_create(telegram_user=telegram_user)[0]
    matrix_of_courses = TfidMatrixAllCourses.objects.all().first().matrix
    output = []
    cosine_similarities = linear_kernel(matrix_of_courses[np.random.randint(0,matrix_of_courses.shape[0]-1)],
                                        matrix_of_courses).flatten()
    list_of_indexes = np.linspace(cosine_similarities.min(), cosine_similarities.max(), num=15)
    for each in list_of_indexes:
        test_course = find_nearest(cosine_similarities, each)
        if not test_course in output:
            output.append(test_course)
    print output
    test_courses.save_list(output)


def i_am_going_to_teach_you(telegram_id, answer_id, is_right = False, teaching_coeff = 0.01 ):
    telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
    learn_vector = TfidUserVector.objects.get(telegram_user=telegram_user)
    course_matrix = TfidMatrixAllCourses.objects.all().first().matrix
    answer = course_matrix[answer_id]
    for each in answer.indices:
        if each in learn_vector.vector.indices:
            learn_index = np.where(learn_vector.vector.indices == each)[0][0]
            answer_index = np.where(answer.indices == each)[0][0]
            if is_right:
                learn_vector.vector.data[learn_index] = learn_vector.vector.data[learn_index] + np.float64(teaching_coeff)
            else:
                learn_vector.vector.data[learn_index] = learn_vector.vector.data[learn_index] - np.float64(teaching_coeff)
    learn_vector.save()


def prediction(telegram_id):
    telegram_user = EdxTelegramUser.objects.get(telegram_id=telegram_id)
    results = CourseEnrollment.enrollments_for_user(telegram_user.student)
    course_matrix = TfidMatrixAllCourses.objects.all().first().matrix
    list_of_user_courses_indexes = [MatrixEdxCoursesId.objects.get(course_key=course.course_id).course_index
                                    for course in results]

    user_vector = TfidUserVector.objects.get(telegram_user=telegram_user)
    cosine_similarities = linear_kernel(user_vector.vector, course_matrix).flatten()

    #removing courses on which user already enrolled
    if len(list_of_user_courses_indexes) == len(cosine_similarities):
        return -1
    cosine_similarities[list_of_user_courses_indexes] = -1000

    related_docs_indices = cosine_similarities.argsort()
    #TODO uncomment when it will enough courses
    # little_random = np.random.randint(5,10)
    # print little_random
    # return related_docs_indices[-little_random]
    return 0


