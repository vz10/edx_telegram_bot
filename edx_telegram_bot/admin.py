'''
django admin pages for edx-telegram bot model
'''

from models import (EdxTelegramUser, TfidMatrixAllCourses, MatrixEdxCoursesId,
                    TfidUserVector, LearningPredictionForUser, PredictionForUser)
from ratelimitbackend import admin


class EdxTelegramUserAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'telegram_id', 'created', 'modified')
    list_filter = ('student', 'status')
    readonly_fields = ('hash',)

admin.site.register(EdxTelegramUser)
admin.site.register(TfidMatrixAllCourses)
admin.site.register(MatrixEdxCoursesId)
admin.site.register(TfidUserVector)
admin.site.register(LearningPredictionForUser)
admin.site.register(PredictionForUser)

class LearningPredictionForUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_user', 'prediction_list')
    list_filter = ('telegram_user', 'prediction_list')


admin.site.register(EdxTelegramUser, EdxTelegramUserAdmin)
admin.site.register(LearningPredictionForUser, LearningPredictionForUserAdmin)

