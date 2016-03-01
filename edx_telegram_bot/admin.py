'''
django admin pages for edx-telegram bot model
'''

from models import (EdxTelegramUser, TfidMatrixAllCourses, MatrixEdxCoursesId,
                 TfidUserVector, LearningPredictionForUser, PredictionForUser,
                 UserCourseProgress, BotFriendlyCourses)
from ratelimitbackend import admin


class EdxTelegramUserAdmin(admin.ModelAdmin):
    """
    Admin CRUD for EdxTelegramUser model
    """
    list_display = ('student', 'status', 'telegram_id', 'created', 'modified')
    list_filter = ('student', 'status')
    readonly_fields = ('hash',)


class LearningPredictionForUserAdmin(admin.ModelAdmin):
    """
    Admin CRUD for LearningPredictionForUser model
    """
    list_display = ('telegram_user', 'prediction_list')
    list_filter = ('telegram_user', 'prediction_list')


admin.site.register(EdxTelegramUser, EdxTelegramUserAdmin)
admin.site.register(LearningPredictionForUser, LearningPredictionForUserAdmin)

admin.site.register(TfidMatrixAllCourses)
admin.site.register(MatrixEdxCoursesId)
admin.site.register(TfidUserVector)
admin.site.register(PredictionForUser)
admin.site.register(UserCourseProgress)
admin.site.register(BotFriendlyCourses)
