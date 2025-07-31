from django.urls import path
from . import views

urlpatterns = [
     path('', views.home, name='home'),  # Optional Home C:\Users\admin\quantcrypt\wev\templates\about.html Page
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    path('courses/', views.courses, name='courses'),
    path('register/', views.register, name='register'),
    path('billing/<int:reg_id>/', views.billing, name='billing'),


]
