from django.contrib import admin
from .models import Course, Registration

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'course', 'plan', 'has_discount')
    list_filter = ('course', 'plan', 'has_discount')
    search_fields = ('name', 'email', 'phone', 'referral_code')
