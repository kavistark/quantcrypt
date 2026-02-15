from rest_framework import serializers
from .models import Course, Registration, ProgramRegister, ServiceInterest


# -------------------------
# Course Serializer
# -------------------------
class CourseSerializer(serializers.ModelSerializer):
    tools_list = serializers.SerializerMethodField()
    projects_list = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'name',
            'tools',
            'projects',
            'tools_list',
            'projects_list',
        ]

    def get_tools_list(self, obj):
        return obj.tools_list()

    def get_projects_list(self, obj):
        return obj.projects_list()


# -------------------------
# Registration Serializer
# -------------------------
class RegistrationSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'course',
            'course_name',
            'plan',
            'referral_code',
            'has_discount',
        ]

    def validate_email(self, value):
        """
        Prevent duplicate registrations using same email
        """
        if Registration.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value


# -------------------------
# Program Register Serializer
# -------------------------
class ProgramRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramRegister
        fields = [
            'id',
            'name',
            'year',
            'college',
            'number',
            'email',
            'registered_at',
        ]
        read_only_fields = ['registered_at']


# -------------------------
# Service Interest Serializer
# -------------------------
class ServiceInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceInterest
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'service',
            'message',
            'created_at',
        ]
        read_only_fields = ['created_at']
