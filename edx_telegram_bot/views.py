import json
from bson.objectid import ObjectId

from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

from xmodule.modulestore.django import modulestore
from bot_mongo import BotMongo

@login_required
def courses_list(request):
     results = modulestore().get_courses()
     results = [course for course in results if
     course.scope_ids.block_type == 'course']
     courses = [[course.id, modulestore().get_course(course.id).display_name_with_default] for course in results]
     return render(request,'bot/courses_list.html',context={'courses':courses})

@login_required
def course_nods(request, course_key_string):
    connection = BotMongo(database='bot',collection=course_key_string)
    if request.method == 'POST':
        json_dict =  request.POST.dict()
        print json_dict
        del json_dict['csrfmiddlewaretoken']
        json_dict["_id"] = ObjectId(json_dict["_id"])
        connection.upsert(json_dict)

    course_steps = connection.find_all()
    return render(request,'bot/courses_steps.html',context={'steps':course_steps})
