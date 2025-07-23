from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('register/', views.register, name='register'),
    path('billing/<int:reg_id>/', views.billing, name='billing'),
    path('payment-gateway/', views.payment_gateway, name='payment_gateway'),
]
