from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=100)
    tools = models.TextField(help_text="Comma-separated list of tools", blank=True)
    projects = models.TextField(help_text="Comma-separated list of projects", blank=True)

    def __str__(self):
        return self.name

    def tools_list(self):
        return [tool.strip() for tool in self.tools.split(',') if tool.strip()]

    def projects_list(self):
        return [project.strip() for project in self.projects.split(',') if project.strip()]


class Registration(models.Model):
    PLAN_CHOICES = [
        ('Standard', 'Standard Plan'),
        ('Advanced', 'Advanced Plan'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    referral_code = models.CharField(max_length=50, blank=True, null=True)
    has_discount = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.course.name}"
