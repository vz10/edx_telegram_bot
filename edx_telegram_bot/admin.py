'''
django admin pages for edx-telegram bot model
'''
from django import forms
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.locator import CourseLocator

from models import (EdxTelegramUser, TfidMatrixAllCourses, MatrixEdxCoursesId,
                    TfidUserVector, LearningPredictionForUser, PredictionForUser,
                    UserCourseProgress, BotFriendlyCourses, UserLocation)
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


class BotFriendlyCoursesAdminForm(forms.ModelForm):
    class Meta:
        model = BotFriendlyCourses
        fields = ('token', 'course_key')

    def __init__(self, *args, **kwargs):
        super(BotFriendlyCoursesAdminForm, self).__init__(*args, **kwargs)
        results = modulestore().get_courses()
        course_list = [(course.id, course.id) for course in results if course.scope_ids.block_type == 'course']
        self.fields['course_key'] = forms.ChoiceField(choices=course_list)


class BotFriendlyCoursesAdmin(admin.ModelAdmin):
    list_display = ('bot_name', 'course_key')

    form = BotFriendlyCoursesAdminForm


admin.site.register(EdxTelegramUser, EdxTelegramUserAdmin)
admin.site.register(LearningPredictionForUser, LearningPredictionForUserAdmin)

admin.site.register(TfidMatrixAllCourses)
admin.site.register(MatrixEdxCoursesId)
admin.site.register(TfidUserVector)
admin.site.register(PredictionForUser)
admin.site.register(UserCourseProgress)
admin.site.register(BotFriendlyCourses, BotFriendlyCoursesAdmin)
admin.site.register(UserLocation)
