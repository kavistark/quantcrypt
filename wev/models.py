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

from django.db import models

class ServiceInterest(models.Model):

    SERVICE_CHOICES = [
        ('web-development', 'Web Development'),
        ('mobile-app', 'Mobile App Development'),
        ('ecommerce', 'E-commerce Solutions'),
        ('digital-marketing', 'Digital Marketing'),
        ('seo', 'SEO Services'),
        ('consulting', 'Technical Consulting'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProgramRegister(models.Model):
    YEAR_CHOICES = [
        ('1st Year', '1st Year'),
        ('2nd Year', '2nd Year'),
        ('3rd Year', '3rd Year'),
        ('4th Year', '4th Year'),
        ('Graduated', 'Graduated'),
        ('Working', 'Working Professional'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ]

    name = models.CharField(max_length=150)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    college = models.CharField(max_length=200)
    department = models.CharField(max_length=150)
    year = models.CharField(max_length=30, choices=YEAR_CHOICES)

    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)

    registered_at = models.DateTimeField(auto_now_add=True)
