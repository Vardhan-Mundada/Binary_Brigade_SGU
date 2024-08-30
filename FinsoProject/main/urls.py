from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('send-otp-email/', views.send_otp_email, name='send_otp_email'),
]