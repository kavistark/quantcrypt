from django.urls import path
from . import views

urlpatterns = [
     path('', views.home, name='home'),  # Optional Home C:\Users\admin\quantcrypt\wev\templates\about.html Page
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('offer-program/', views.Offer_Program, name='offer_program'),
    path('courses/', views.courses, name='courses'),
    path('register/', views.register, name='register'),
    path('billing/<int:reg_id>/', views.billing, name='billing'),
    path('program-register/', views.program_register, name='program_register'),
    path('registration-success/', views.registration_success, name='registration_success'),

    path('Web-Development-Services/',views.web_ser,name='Web_Development_Services'),
    path('android-Development-Services/',views.and_ser,name='android_Development_Services'),


]


