from django.contrib import admin
from .models import Course, Registration, ProgramRegister


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_tools', 'display_projects')
    search_fields = ('name', 'tools', 'projects')

    def display_tools(self, obj):
        return ", ".join(obj.tools_list())
    display_tools.short_description = 'Tools'

    def display_projects(self, obj):
        return ", ".join(obj.projects_list())
    display_projects.short_description = 'Projects'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'course', 'plan', 'has_discount', 'referral_code')
    list_filter = ('plan', 'has_discount', 'course')
    search_fields = ('name', 'email', 'phone', 'referral_code')


@admin.register(ProgramRegister)
class ProgramRegisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'year', 'college', 'number', 'registered_at')
    list_filter = ('year', 'registered_at')
    search_fields = ('name', 'email', 'college', 'number')
