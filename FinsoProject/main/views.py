from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib import messages
from django.core.mail import send_mail
from django.core.cache import cache
import random
import string
from django.http import JsonResponse
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()
import os
from .models import ExpenseCategory
from .chatbot.preprocess import preprocess_text
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib

# Create your views here.
def home(request):
    return HttpResponse("Hello, World!")


def user_logout(request):
    logout(request)
    return redirect('home')

def create_default_categories(user):
    default_categories = [
        'Food',
        'Transportation',
        'Utilities',
        'Entertainment',
        'Health',
        'Other'
    ]
    for category_name in default_categories:
        ExpenseCategory.objects.create(user=user, name=category_name)

#register function
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        email = request.POST.get('email')
        phone_no = request.POST.get('phone_no')
        if form.is_valid() and request.POST.get('email_verification_otp') == cache.get(f'email_otp_{email}') and request.POST.get('phone_verification_otp') == cache.get(f'email_otp_{phone_no}'):
            user = form.save()
            create_default_categories(user)
            auth_login(request, user)
            messages.success(request, 'Registration successful.')
            cache.delete(f'email_otp_{email}')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP or form data.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def send_otp_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = generate_otp()
        cache.set(f'email_otp_{email}', otp, timeout=300)  # OTP valid for 5 minutes
        send_mail(
            'Your Email Verification OTP',
            f'Your OTP is {otp}',
            'vardhanbot31@gmail.com',
            [email],
            fail_silently=False,
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def send_otp_mobile(request):
    if request.method == 'POST':
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        phone_no = request.POST.get('phone_no')
        otp = generate_otp()
        cache.set(f'email_otp_{phone_no}', otp, timeout=300)  # OTP valid for 5 minutes
        mess = f"Hello, your OTP is {otp}"
        client = Client(account_sid,auth_token)
        message = client.messages.create( body=mess  , from_="+15179926230", to=phone_no)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('home')  
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body.decode('utf-8'))  # Decode and load the JSON
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'main', 'chatbot', 'chatbot_model.pkl')
            label_encoder_path = os.path.join(base_dir, 'main', 'chatbot', 'label_encoder.pkl')
            model = joblib.load(model_path)
            label_encoder = joblib.load(label_encoder_path)
            user_input = body.get('message', '')
            preprocessed_input = preprocess_text(user_input)
            prediction = model.predict([preprocessed_input])
            intent = label_encoder.inverse_transform(prediction)[0]
            
            # Define response based on intent
            responses = {
                'CategoryWiseExpenseTracking': get_category_response(preprocessed_input),
                'GeneralExpenseTracking': get_category_response(preprocessed_input)
                # Add other intents here
            }
            
            response_message = responses.get(intent, intent)
            
            return JsonResponse({'intent': intent, 'response': response_message})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    elif request.method == 'GET':
        return render(request, 'chatbot.html')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_category_response(preprocessed_input):
    if "top 5" in preprocessed_input or "highest spending" in preprocessed_input or "rank" in preprocessed_input:
        return "Here are the top 5 categories by spending: [Top categories details]"
    
    categories = ['entertainment', 'groceries', 'utilities', 'transportation', 'dining', 'food']
    preprocessed_categories = [preprocess_text(category) for category in categories]
    for category in preprocessed_categories:  
        if category in preprocessed_input:
            original_category = categories[preprocessed_categories.index(category)]
            return f"Here’s the spending for {original_category}: [Specific category details]"
    
    return "Here’s a general breakdown of your expenses."