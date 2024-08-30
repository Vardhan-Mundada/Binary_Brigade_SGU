from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    return HttpResponse("Hello, World!")

def login(request):
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    return render(request, 'register.html')