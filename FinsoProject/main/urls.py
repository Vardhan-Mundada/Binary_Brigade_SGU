from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('send-otp-email/', views.send_otp_email, name='send_otp_email'),
    path('send-otp-mobile/', views.send_otp_mobile, name='send_otp_mobile'),
    path('chatbot/', views.chatbot, name='chatbot')
]