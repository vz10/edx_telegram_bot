'''
django admin pages for edx-telegram bot model
'''

from models import EdxTelegramUser, TfidMatrixAllCourses, MatrixEdxCoursesId, TfidUserVector, LearningPredictionForUser
from ratelimitbackend import admin

admin.site.register(EdxTelegramUser)
admin.site.register(TfidMatrixAllCourses)
admin.site.register(MatrixEdxCoursesId)
admin.site.register(TfidUserVector)
admin.site.register(LearningPredictionForUser)




