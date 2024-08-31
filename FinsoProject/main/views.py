from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, IncomeForm , ExpenseForm, CategoryForm, RecurringExpenseForm, UserProfileForm
from django.contrib import messages
from django.core.mail import send_mail
from django.core.cache import cache
import random
from django.contrib.auth.decorators import login_required
import string
from django.http import JsonResponse
from twilio.rest import Client
from datetime import datetime, time
from django.utils import timezone
from django.contrib.auth.models import User, AnonymousUser
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'FinsoProject', '.env')

load_dotenv(dotenv_path)
import os
from .models import ExpenseCategory, Transaction, Income, UserProfile
from django.db.models.functions import Coalesce
from django.db.models import Value, DecimalField ,Sum
from django.utils import timezone
from .models import Stock, MutualFund, FixedDeposit
import requests
from .models import Stock, MutualFund, FixedDeposit
from django.core.paginator import Paginator


#SMS
import re
from pyrebase import pyrebase
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
config = {
    "apiKey": "AIzaSyAgOa_2ruLNE0Imc9y4cidhc7mls16M22Y",
    "authDomain": "hack-b201c.firebaseapp.com",
    "databaseURL": "https://hack-b201c-default-rtdb.firebaseio.com",
    "projectId": "hack-b201c",
    "storageBucket": "hack-b201c.appspot.com",
    "messagingSenderId": "143352711844",
    "appId": "1:143352711844:web:ef84abbea711bb46edb431",
    "measurementId": "G-4HVL7F6SHC"
}

firebase = pyrebase.initialize_app(config)
database = firebase.database()


def determine_transaction_type(message):
    message_lower = message.lower()
    if any(keyword in message_lower for keyword in ["debited", "debit", "withdrawn", "transferred from A/c"]):
        return "debited"
    elif any(keyword in message_lower for keyword in ["credited", "credit", "deposited"]):
        return "credited"
    return "unknown"

def is_financial_message(message):
    # Keywords associated with financial transactions
    financial_keywords = [
        "debited", "debit", "withdrawn","credited", "credit", "deposited"
    ]

    bank_words=[
        "-ICICI","-BOB","-SBI","Bank of Baroda",
        "Bank of India","BOI"
        "Canara Bank",
        "Central Bank of India","Indian Overseas Bank",
        "Union Bank of India","CITI","Axis","Bandhan",
        "DCB","Federal Bank","HDFC","Dhanlaxmi","IDFC","Kotak Mahindra",
        "Yes Bank"
    ]
    
    # Regular expressions for common financial patterns
    amount_pattern = r'(?:rs\.?|inr)\s?(\d+(:?\,\d+)?(:?\.\d{1,2})?)'
    account_pattern = r'a/c|account\s?:?\s?\d+'
    upi_pattern = r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b'
    
    message_lower = message.lower()
    
    # Check for financial keywords
    has_financial_keyword = any(keyword in message_lower for keyword in financial_keywords)
    has_bank_words = any(keyword in message_lower for keyword in bank_words)
    
    # Check for financial patterns
    has_amount = bool(re.search(amount_pattern, message_lower))
    has_account_ref = bool(re.search(account_pattern, message_lower))
    has_upi_id = bool(re.search(upi_pattern, message))
    
    return (has_financial_keyword or has_bank_words) and has_amount or has_account_ref or has_upi_id


def extract_numeric_value(message):
    numeric_pattern = r"\b(?:Rs\.?|Rs|\u20B9)\s?(\d+\.?\d*)\b"
    match = re.search(numeric_pattern, message)
    if match:
        return match.group(1)  
    return None


import pickle
from sklearn.feature_extraction.text import CountVectorizer
from django.conf import settings
import os
 #Load the models and vectorizer
base_dir = settings.BASE_DIR
model_dir = os.path.join(base_dir, 'main')


logistic_model = pickle.load(open(os.path.join(model_dir, "logistic_regression_model.pkl"), "rb"))
naivebayes_model = pickle.load(open(os.path.join(model_dir, "naivebayes_model.pkl"), "rb"))
randomforest_model = pickle.load(open(os.path.join(model_dir, "randomforest_model.pkl"), "rb"))
vectorizer = pickle.load(open(os.path.join(model_dir, "vectorizer.pkl"), "rb"))
def is_spam(message_content):
    transformed_text = vectorizer.transform([message_content])

    # Make predictions using the loaded models
    prediction_logistic = logistic_model.predict(transformed_text)[0]
    prediction_naivebayes = naivebayes_model.predict(transformed_text)[0]
    prediction_randomforest = randomforest_model.predict(transformed_text)[0]

    # If any model predicts spam (1), return True
    if 1 in [prediction_logistic, prediction_naivebayes, prediction_randomforest]:
        return True
    else:
        return False
def list_of_message(message_list):
    processed_messages = []
    spamList = ["AJIOIN", "ZEPTON", "KHELMR",
                "ARWGOV", "EATSRE", "NCDMAS",
                "CRESCT", "ATRLTV", "SWIGGY",
                "SMACAR", "ECROMA"
               ]
    for message in message_list:
        parts = message.split(';')
        sender = parts[0].split(':')[1]
        time = parts[1][5:]
        message_content = parts[2].split(':')[1]
        
        if sender[3:] in spamList:
            continue
        
        if is_spam(message_content):
            continue
        
        if is_financial_message(message_content):
            transaction_type = determine_transaction_type(message_content)
            numeric_value = extract_numeric_value(message_content)
            processed_messages.append([sender, time, message_content, transaction_type, (numeric_value)])

    return processed_messages


from django.utils import timezone
from .models import Transaction, ExpenseCategory
from decimal import Decimal

def add_to_db(processed_messages, request):
    user = request.user
    if isinstance(user, AnonymousUser):
        print("User is not authenticated. Cannot add transactions.")
        return
    

    for msg in processed_messages:
        _, time_str, message_content, transaction_type, amount = msg

        try:
            # Convert amount to Decimal
            print(f"Amount: {amount}")
            amount = Decimal(str(amount))

            # Parse the transaction date
            transaction_date = timezone.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            # Create the transaction
            new_transaction = Transaction.objects.create(
                user=user,
                amount=amount,
                type=transaction_type,
                notes=message_content,
                category=ExpenseCategory.objects.get(id=6),
                # transaction_date=transaction_date
            )
            print(f"Transaction added: {new_transaction}")
        except Exception as e:
            print(f"Error adding transaction: {str(e)}")

    print("All transactions processed")


def transfer_messages_from_firebase_to_db(request):
    user= UserProfile.objects.get(user=request.user)
    mobile_number = "+91" + user.phone_no
    # mobile_number = "+919999999999"
    message_list = []
    try:
        messages = database.child("Users").child(mobile_number).child("messages").get().val()

        if messages:
            print("Messages found")
            message_list = [msg for msg in messages.values()]
        else:
            print("No messages found for this number")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    processed_messages = list_of_message(message_list)
    add_to_db(processed_messages, request)
    database.child("Users").child(mobile_number).child("messages").remove()
    return processed_messages




from .chatbot.preprocess import preprocess_text
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib

# Create your views here.
def home(request):
    # return HttpResponse("Hello, World!")
    return render(request, 'home.html')


def user_logout(request):
    logout(request)
    return redirect('home')

def create_default_categories(user):
    default_categories = [
        'Food',
        'Transportation',
        'Entertainment',
        'Health',
        'Miscellaneous',
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
            return redirect('analytics')
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
            list_of_msgs=transfer_messages_from_firebase_to_db(request)
            print(list_of_msgs)
            # add_to_db(list_of_msgs, request)

            return redirect('analytics')  
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


#expense feature
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def analytics(request):
    time_interval = request.GET.get('time_interval', 'weekly')
    end_date = timezone.now().date()

    if time_interval == 'weekly':
        start_date = end_date - timezone.timedelta(days=7)
    elif time_interval == 'monthly':
        start_date = end_date - timezone.timedelta(days=30)
    elif time_interval == '3months':
        start_date = end_date - timezone.timedelta(days=90)
    elif time_interval == '6months':
        start_date = end_date - timezone.timedelta(days=180)
    elif time_interval == 'yearly':
        start_date = end_date - timezone.timedelta(days=365)
    else:
        start_date = end_date

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    expenses = Transaction.objects.filter(user=request.user, transaction_date__range=[start_datetime, end_datetime])
    categories = expenses.values_list('category__name', flat=True).distinct()

    total_income = Income.objects.filter(user=request.user).aggregate(total_income=Sum('amount'))['total_income'] or 0
    total_expenses = expenses.aggregate(total_expenses=Sum('amount'))['total_expenses'] or 0
    remaining_amount = total_income - total_expenses

    category_totals = (
        Transaction.objects.filter(user=request.user, transaction_date__range=[start_datetime, end_datetime])
        .values('category__name')
        .annotate(
            total_expenses=Coalesce(
                Sum('amount'), 
                Value(0, output_field=DecimalField())
            )
        )
        .order_by('-total_expenses')[:4]
    )

    income_sources = Income.objects.filter(user=request.user).values('source').annotate(total_income=Sum('amount')).order_by('-total_income')
    
    expense_sources = (
        Transaction.objects.filter(user=request.user, transaction_date__range=[start_datetime, end_datetime])
        .values('category__name')
        .annotate(total_amount=Sum('amount'))
    )

    expense_sources_data = {
        'categories': list(expense_sources.values_list('category__name', flat=True)),
        'amounts': list(expense_sources.values_list('total_amount', flat=True))
    }
    recent_expenses = Transaction.objects.filter(user=request.user).order_by('-transaction_date')[:7]


    pie_chart = create_pie_chart(request.user, categories, expenses)
    bar_chart = create_bar_chart(request.user, categories, expenses)

    # Prepare income source data for frontend
    income_sources_data = {
        'sources': [source['source'] for source in income_sources],
        'amounts': [source['total_income'] for source in income_sources]
    }
    predefined_categories = [
        {'name': 'Food', 'icon': 'icons/food.png'},
        {'name': 'Transportation', 'icon': 'icons/transportation.png'},
        {'name': 'Entertainment', 'icon': 'icons/entertainment.png'},
        {'name': 'Health', 'icon': 'icons/health.png'},
        {'name': 'Miscellaneous', 'icon': 'icons/miscellaneous.png'}
    ]
    context = {
        'time_interval': time_interval,
        'categories': categories,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'income_sources_data': json.dumps(income_sources_data, cls=DjangoJSONEncoder),  # Add this line
        'total_income': total_income,
        'total_expenses': total_expenses,
        'remaining_amount': remaining_amount,
        'recent_expenses': recent_expenses,
        'category_totals': category_totals,
        'expense_sources_data': json.dumps(expense_sources_data, cls=DjangoJSONEncoder),
        'predefined_categories': predefined_categories,
    }

    return render(request, 'analytics.html', context)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def create_pie_chart(user, categories, expenses):
    category_totals = {category: 0 for category in categories}

    for expense in expenses:
        category_totals[expense.category.name] += expense.amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    plt.figure(figsize=(5, 5))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.6))
    plt.title('Expense Distribution by Category')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    plt.close()

    return image_base64


def create_bar_chart(user, categories, expenses):
    category_totals = {category: 0 for category in categories}
    for expense in expenses:
        category_totals[expense.category.name] += expense.amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    plt.figure(figsize=(6, 5))
    plt.bar(labels, values, color='blue')
    plt.xlabel('Categories')
    plt.ylabel('Total Expense Amount')
    plt.title('Total Expense Amount by Category')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    plt.close()

    return image_base64



#add all
@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('analytics')
    else:
        form = IncomeForm()
    return render(request, 'add_income.html', {'form': form})


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('analytics')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})


@login_required
def category_list(request):
    categories = ExpenseCategory.objects.filter(user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'category_list.html', {'categories': categories, 'form': form})

@login_required
def add_category(request):
    categories = ExpenseCategory.objects.filter(user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('analytics')
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form, 'categories':categories})

@login_required
def addall(request):
    return render(request, 'addall.html')




import pandas as pd

@login_required
def dashboard(request):
    incomes = Income.objects.filter(user=request.user)
    categories = ExpenseCategory.objects.filter(user=request.user)
    recent_expenses = Transaction.objects.filter(user=request.user).order_by('-transaction_date')[:5]
    
    # Fetch investment details
    stocks = Stock.objects.filter(user=request.user)
    mutual_funds = MutualFund.objects.filter(user=request.user)
    fixed_deposits = FixedDeposit.objects.filter(user=request.user)
    
    total_income = incomes.aggregate(total_income=Sum('amount'))['total_income'] or 0
    category_expenses = {}
    
    for category in categories:
        total_expense = Transaction.objects.filter(user=request.user, category=category).aggregate(total_expense=Sum('amount'))['total_expense'] or 0
        category_expenses[category.name] = {
            'limit': category.budget_limit,
            'current_expense': total_expense
        }

    # Calculate current value of stocks
    stock_values = []
    for stock in stocks:
        current_price = 102.6
        current_value = float(current_price) * float(stock.number_of_shares)
        stock_values.append({
            'ticker_symbol': stock.ticker_symbol,
            'current_value': current_value,
            'number_of_shares': stock.number_of_shares,
            'purchase_price_per_share': stock.purchase_price_per_share,
            'date_invested': stock.date_invested
        })

    # Calculate current value of mutual funds
    mutual_fund_values = []
    for mutual_fund in mutual_funds:
        current_nav = get_nav_for_scheme(mutual_fund.name)
        current_value = float(current_nav) * float(mutual_fund.units_purchased)
        mutual_fund_values.append({
            'name': mutual_fund.name,
            'current_value': current_value,
            'units_purchased': mutual_fund.units_purchased,
            'nav_at_purchase': mutual_fund.nav_at_purchase,
            'date_invested': mutual_fund.date_invested
        })

    context = {
        'incomes': incomes,
        'categories': categories,
        'recent_expenses': recent_expenses,
        'category_expenses': category_expenses,
        'total_income': total_income,
        'stocks': stocks,
        'mutual_funds': mutual_funds,
        'fixed_deposits': fixed_deposits,
        'stock_values': stock_values,
        'mutual_fund_values': mutual_fund_values,
    }
    
    return render(request, 'dashboard.html', context)

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.units import inch
from datetime import datetime, timedelta

@login_required
def export_report(request, format='pdf'):
    seven_days_ago = datetime.now() - timedelta(days=7)
    transactions = Transaction.objects.filter(user=request.user, transaction_date__gte=seven_days_ago)

    df = pd.DataFrame(list(transactions.values('transaction_date', 'amount', 'notes', 'category__name')))

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    category_spending = df.groupby('category__name')['amount'].sum()
    category_spending = category_spending[category_spending > 0]

    if format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        styles = getSampleStyleSheet()
        title = Paragraph("Expense Report for the Last 7 Days", styles['Title'])
        summary = Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])

        data = [['Date', 'Amount', 'Notes', 'Category']]
        for index, row in df.iterrows():
            data.append([row['transaction_date'], row['amount'], row['notes'], row['category__name']])

        transaction_table = Table(data, colWidths=[2 * inch, 1.5 * inch, 3 * inch, 1.5 * inch])
        transaction_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        category_data = [['Category', 'Total Expense']]
        for category, amount in category_spending.items():
            category_data.append([category, f'{amount:.2f}'])

        category_table = Table(category_data, colWidths=[3 * inch, 3 * inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        plt.figure(figsize=(6, 3))
        category_spending.plot(kind='bar', color='skyblue')
        plt.title('Category-wise Spending')
        plt.ylabel('Total Amount')
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()
        img_buffer.seek(0)

        report_image = Image(img_buffer, 4.5 * inch, 2.5 * inch)  

        elements = [title, summary, Spacer(1, 12), Paragraph("Transactions:", styles['Heading2']), transaction_table,
                    PageBreak(),  
                    Paragraph("Category-Wise Expenses:", styles['Heading2']), category_table, Spacer(1, 24), report_image]

        doc.build(elements)
        buffer.seek(0)
        response.write(buffer.getvalue())
        buffer.close()

        return response


    
def parse_time_period(preprocessed_input):
    """ Parses the time period from the user input using regex. """
    now = datetime.now()
    
    # Define regex patterns for various time periods
    patterns = {
        r'last 30 days': now - timedelta(days=30),
        r'last month': now.replace(day=1) - timedelta(days=1),
        r'this month': now.replace(day=1),
        r'last 3 months': now - timedelta(days=90),
        r'this year': now.replace(month=1, day=1),
        r'last year': now.replace(year=now.year - 1, month=1, day=1),
        r'past week': now - timedelta(days=7),
    }
    
    for pattern, start_date in patterns.items():
        if re.search(pattern, preprocessed_input, re.IGNORECASE):
            return start_date
    
    # Default case if no pattern matched
    return None
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
            
            responses = {
                'CategoryWiseExpenseTracking': get_category_response(preprocessed_input),
                'IncomeManagement' : get_income_management_response(preprocessed_input,request),
                'InvestmentTracking' : get_investment_tracking_response(preprocessed_input,request),
                # 'AnalyticsAndGraphs' : get_analytics_response(preprocessed_input),
                'BudgetManagement' : get_budget_management(preprocessed_input,request)
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
            sd = parse_time_period(preprocessed_input)
            if sd is not None:
                days = timezone.now() - sd
            else:
                days = 30
            transactions = get_transactions_by_category_and_days(original_category,days)
            
            if transactions:
                # Format transactions for display as an HTML table
                table_rows = "\n".join(
                    [f"<tr><td>{transaction.id}</td><td>{transaction.amount}</td><td>{transaction.transaction_date.strftime('%Y-%m-%d')}</td><td>{transaction.notes}</td></tr>"
                     for transaction in transactions]
                )
                table_html = f"""
                <table border="1" cellpadding="5" cellspacing="0" style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>Transaction ID</th>
                            <th>Amount</th>
                            <th>Date</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                """
                return f"Here are your transactions for the category '{original_category}' of past {days} :<br>{table_html}"
            else:
                return f"No transactions found for the category '{original_category}' in the specified time period."

    return "Here’s a general breakdown of your expenses."


def get_income_management_response(text, request):
    # Get data from the Income model
    incomes = Income.objects.filter(user=request.user)
    total_income = incomes.aggregate(total_income=Sum('amount'))['total_income'] or 0
    
    # Create an HTML table
    table_html = '<table border="1">'
    table_html += '<tr><th>Source</th><th>Amount</th><th>Date</th></tr>'
    
    for income in incomes:
        table_html += f'<tr><td>{income.source}</td><td>{income.amount}</td><td>{income.date}</td></tr>'
    
    table_html += '</table>'
    table_html += f'<p><strong>Total Income: </strong>{total_income}</p>'
    
    return table_html   

def get_investment_tracking_response(preprocessed_input, request):
    # Get data from the investment models
    stocks = Stock.objects.filter(user=request.user)
    mutual_funds = MutualFund.objects.filter(user=request.user)
    fixed_deposits = FixedDeposit.objects.filter(user=request.user)
    
    # Initialize total investment sum
    total_investment = 0
    
    # Create an HTML table
    table_html = '<table border="1">'
    table_html += '<tr><th>Investment Type</th><th>Name</th><th>Amount</th><th>Date</th></tr>'
    
    # Add stocks to the table
    for stock in stocks:
        total_stock_value = stock.number_of_shares * stock.purchase_price_per_share
        table_html += f'<tr><td>Stock</td><td>{stock.ticker_symbol}</td><td>{total_stock_value:.2f}</td><td>{stock.date_invested}</td></tr>'
        total_investment += total_stock_value
    
    # Add mutual funds to the table
    for fund in mutual_funds:
        total_fund_value = fund.units_purchased * fund.nav_at_purchase
        table_html += f'<tr><td>Mutual Fund</td><td>{fund.name}</td><td>{total_fund_value:.2f}</td><td>{fund.date_invested}</td></tr>'
        total_investment += total_fund_value
    
    # Add fixed deposits to the table
    for deposit in fixed_deposits:
        table_html += f'<tr><td>Fixed Deposit</td><td>{deposit.bank_name}</td><td>{deposit.amount_invested:.2f}</td><td>{deposit.date_invested}</td></tr>'
        total_investment += deposit.amount_invested
    
    table_html += '</table>'
    table_html += f'<p><strong>Total Investment: </strong>{total_investment:.2f}</p>'
    
    return table_html


from django.db.models import Sum
from django.utils import timezone

def get_budget_management(preprocessed_input, request):
    # Get data from the ExpenseCategory model
    categories = ExpenseCategory.objects.filter(user=request.user)
    
    # Initialize the HTML table
    table_html = '<table border="1">'
    table_html += '<tr><th>Category</th><th>Spending</th><th>Budget Limit</th><th>Status</th></tr>'
    
    for category in categories:
        # Calculate total spending for each category
        total_spending = Transaction.objects.filter(
            user=request.user,
            category=category,
            type='expense'
        ).aggregate(total_spent=Sum('amount'))['total_spent'] or 0
        
        # Determine if the category is over budget
        if total_spending > category.budget_limit:
            status = f'Over budget by {total_spending - category.budget_limit:.2f}'
        else:
            status = f'Within budget, {category.budget_limit - total_spending:.2f} left'
        
        # Add a row to the table for each category
        table_html += f'<tr><td>{category.name}</td><td>{total_spending:.2f}</td><td>{category.budget_limit:.2f}</td><td>{status}</td></tr>'
    
    table_html += '</table>'
    
    return table_html



def get_user_investments(user):
    stocks = Stock.objects.filter(user=user)
    mutual_funds = MutualFund.objects.filter(user=user)
    fixed_deposits = FixedDeposit.objects.filter(user=user)

    all_investments = {
        'stocks': stocks,
        'mutual_funds': mutual_funds,
        'fixed_deposits': fixed_deposits
    }

    return all_investments



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Transaction, ExpenseCategory

@login_required
def update_transaction_category(request):
    user = request.user
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        new_category_id = request.POST.get('category')
        
        try:
            transaction = Transaction.objects.get(id=transaction_id, user=user)
            new_category = ExpenseCategory.objects.get(id=new_category_id, user=user)
            transaction.category = new_category
            transaction.save()
            return redirect('update_transaction_category') 
        except (Transaction.DoesNotExist, ExpenseCategory.DoesNotExist):
            pass  

    transactions = Transaction.objects.filter(user=user, category__name='Miscellaneous')
    categories = ExpenseCategory.objects.filter(user=user)

    return render(request, 'update_transactions.html', {
        'transactions': transactions,
        'categories': categories
    })


from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Transaction

def transactions_for_past_days(request, num_days):
    user = request.user 
    end_date = timezone.now()
    start_date = end_date - timedelta(days=num_days)
    
    transactions = Transaction.objects.filter(
        user=user,
        transaction_date__range=[start_date, end_date]
    ).order_by('-transaction_date')
    
    context = {
        'transactions': transactions,
        'num_days': num_days,
    }
    return render(request, 'transactions_for_past_days.html', context)


from django.utils import timezone
from datetime import timedelta

def get_transactions_by_category_and_days(category_name, days=30):
    now = timezone.now()
    start_date = now - timedelta(days=days)
    categories = ExpenseCategory.objects.filter(name=category_name)
    if not categories:
        return []  
    transactions = Transaction.objects.filter(
        category__in=categories,
        transaction_date__gte=start_date
    )
    return transactions


def get_nav_for_scheme(scheme_name):
    file_path = os.path.join(base_dir, 'main','mutual_funds.json') 
    # Read the data from the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Find the NAV for the given scheme name
    for item in data:
        if item["Scheme_Name"] == scheme_name:
            return item["Net_Asset_Value"]
    
    return None


#Recurring Bills
from .models import RecurringExpense
from .forms import RecurringExpenseForm

@login_required
def add_recurring_expense(request):
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('add_recurring_expense')
    else:
        form = RecurringExpenseForm()
    
    # Retrieve the 8 most recent recurring expenses
    recurring_expenses = RecurringExpense.objects.filter(user=request.user).order_by('-start_date')[:8]
    
    return render(request, 'add_recurring_expense.html', {'form': form, 'recurring_expenses': recurring_expenses})


import joblib
from .forms import ImageUploadForm
import pytesseract
from PIL import Image
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
import nltk

svm_model = joblib.load('svm_model.pkl')
tfidf_vectorizer = joblib.load('tfidf_vectorizer.pkl')


def extract_text_from_image(image):
    img = Image.open(image)
    text = pytesseract.image_to_string(img)
    return text


def extract_highest_amount(text):
    lines = [line for line in text.split('\n') if not re.search(r'\b\d{2}\.\d{2}\.\d{4}\b|\bBill\s+No\.\s*\d+\b', line)]

    amounts = []
    for line in lines:
        nums = re.findall(r'\b\d+(?:\.\d+)?\b', line)
        amounts.extend(map(float, nums))

    if amounts:
        return max(amounts)
    else:
        return None
    

def predict_category(text):
    text_tfidf = tfidf_vectorizer.transform([text])
    predicted_category = svm_model.predict(text_tfidf)[0]
    return predicted_category


def billamount(request):
    if request.method == 'POST' and request.FILES['image']:
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            image = request.FILES['image']
            text = extract_text_from_image(image)
            print(text)
            highest_amount = extract_highest_amount(text)
            category_name = predict_category(text)
            print("Highest Amount:", highest_amount)
            print("Category:", category_name)

            category, created = ExpenseCategory.objects.get_or_create(
                    user=user,
                    name=category_name
                )

            user=User.objects.get(id=request.user.id)
            print(user.id)
            if highest_amount and category_name:
                expense = Transaction.objects.create(
                   user=user,
                    amount=highest_amount,
                    category=category,
                    type='debited',
                    notes=f"Expense for {category_name}"
                )
                expense.save()
            return redirect('analytics')

    else:
        form = ImageUploadForm()
    return render(request, 'upload_receipt.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ExpenseCategory, Transaction
from django.db.models import Sum

@login_required
def notifications(request):
    user = request.user
    categories = ExpenseCategory.objects.filter(user=user)
    notifications = []

    for category in categories:
        print(category)
        total_expenses = Transaction.objects.filter(
            user=user,
            category=category
        ).aggregate(total=Sum('amount'))['total'] or 0 
        
        print(total_expenses)

        if total_expenses > category.budget_limit:
            notifications.append({
                'category': category.name,
                'budget_limit': category.budget_limit,
                'current_expenses': total_expenses,
                'overspend': total_expenses - category.budget_limit
            })

    return render(request, 'notifications.html', {'notifications': notifications})



def get_nav_by_scheme_name(scheme_name):
    
    url = os.getenv('MUTUAL_FUNDS_API')
    
    headers = {
        "x-rapidapi-key": os.getenv('MUTUAL_FUNDS_API_KEY'),
        "x-rapidapi-host": os.getenv('MUTUAL_FUNDS_API_HOST')
    }
    querystring = {"Scheme_Type":"Open"}
    api_response = requests.get(url, headers=headers, params=querystring)
    if isinstance(api_response, requests.models.Response):
        api_response = api_response.json()  # Directly parse JSON content
    
    # If api_response is a bytes object, decode and parse JSON
    elif isinstance(api_response, bytes):
        api_response = json.loads(api_response.decode('utf-8'))
    
    # If api_response is a string, parse it directly
    elif isinstance(api_response, str):
        api_response = json.loads(api_response)
    
    # Iterate over the list of schemes to find the matching one
    for scheme in api_response:
        if scheme['Scheme_Name'] == scheme_name:
            return scheme['Net_Asset_Value']
    return None

def getCurrentStockValue(symbol):
    api_key = os.getenv('ALPHA_API_KEY')
    # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=demo
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    print(data)
    time_series = data["Time Series (Daily)"]
    latest_date = next(iter(time_series))
    latest_data = time_series[latest_date]

    # Extracting the close price
    latest_close_price = latest_data["4. close"]

    return latest_close_price

@login_required
def add_stock(request):
    if request.method == 'POST':
        ticker_symbol = request.POST['ticker_symbol']
        number_of_shares = request.POST['number_of_shares']
        purchase_price_per_share = request.POST['purchase_price_per_share']
        date_invested = request.POST['date_invested']

        Stock.objects.create(
            user=request.user,
            ticker_symbol=ticker_symbol,
            number_of_shares=number_of_shares,
            purchase_price_per_share=purchase_price_per_share,
            date_invested=date_invested
        )
        print('data added in fd')
        # return redirect('dashboard')

    return render(request, 'add_stock.html')

@login_required
def add_mutual_fund(request):
    if request.method == 'POST':
        name = request.POST['name']
        units_purchased = request.POST['units_purchased']
        nav_at_purchase = request.POST['nav_at_purchase']
        date_invested = request.POST['date_invested']

        MutualFund.objects.create(
            user=request.user,
            name=name,
            units_purchased=units_purchased,
            nav_at_purchase=nav_at_purchase,
            date_invested=date_invested
        )
        print('data added in fd')


        # return redirect('dashboard')

    # Fetch mutual fund names from API
    # url = os.getenv('MUTUAL_FUNDS_API')
    # headers = {
    #     "x-rapidapi-key": os.getenv('MUTUAL_FUNDS_API_KEY'),
    #     "x-rapidapi-host": os.getenv('MUTUAL_FUNDS_API_HOST')
    # }
    # querystring = {"Scheme_Type": "Open"}
    # api_response = requests.get(url, headers=headers, params=querystring).json()

    # funds = [scheme['Scheme_Name'] for scheme in api_response]
    fund_path = os.path.join(base_dir, 'main', 'mutual_funds.json')

    with open(fund_path, 'r') as file:
        data = json.load(file)
    funds = [item["Scheme_Name"] for item in data]
    return render(request, 'add_mutual_fund.html', {'funds': funds})

@login_required
def add_fixed_deposit(request):
    if request.method == 'POST':
        bank_name = request.POST['bank_name']
        amount_invested = request.POST['amount_invested']
        interest_rate = request.POST['interest_rate']
        date_invested = request.POST['date_invested']
        maturity_date = request.POST['maturity_date']

        FixedDeposit.objects.create(
            user=request.user,
            bank_name=bank_name,
            amount_invested=amount_invested,
            interest_rate=interest_rate,
            date_invested=date_invested,
            maturity_date=maturity_date
        )
        print('data added in fd')
        # return redirect('dashboard')

    return render(request, 'add_fixed_deposit.html')

from django.shortcuts import render, redirect
from .forms import UserProfileForm
from .models import UserProfile

def profile_view(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect after saving to avoid re-submission on refresh
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'form': form,
    })

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=user_profile)
    
    context = {
        'form': form,
        'user_profile': user_profile,
    }
    return render(request, 'profile.html', context)
@login_required
def transactions_list(request):
    # Get the transactions for the logged-in user
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')

    # Paginate transactions
    paginator = Paginator(user_transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Replace 'unknown' with 'debited'
    for transaction in page_obj.object_list:
        if transaction.type == 'unknown':
            transaction.type = 'debited'

    return render(request, 'transactions_list.html', {'page_obj': page_obj})

@login_required
def charts_view(request):
    # Get the last 30 days of transactions
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=29)
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    
    transactions = Transaction.objects.filter(
        user=request.user,
        transaction_date__range=[start_datetime, end_datetime]
    )

    # Prepare data for charts
    dates = []
    credited = []
    debited = []
    total_credited = 0
    total_debited = 0

    for i in range(30):
        current_date = start_date + timedelta(days=i)
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        day_credited = transactions.filter(
            transaction_date__date=current_date,
            type__in=['credited', 'income']  # Include both 'credited' and 'income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        day_debited = transactions.filter(
            transaction_date__date=current_date,
            type__in=['debited', 'debit', 'expense']  # Include 'debited', 'debit', and 'expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        credited.append(float(day_credited))
        debited.append(float(day_debited))
        
        total_credited += day_credited
        total_debited += day_debited

    # Handle 'unknown' type transactions
    unknown_transactions = transactions.filter(type='unknown')
    unknown_total = unknown_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    print(dates)
    print(credited)
    print(debited)

    context = {
        'dates': json.dumps(dates),
        'credited': json.dumps(credited),
        'debited': json.dumps(debited),
        'total_credited': json.dumps(float(total_credited)),
        'total_debited': json.dumps(float(total_debited)),
        'unknown_total': json.dumps(float(unknown_total)),
    }

    return render(request, 'charts.html', context)

from django.shortcuts import render

def minimize_cash_flow(request):
    if request.method == 'POST':
        transactions_input = request.POST.get('transactions', '')
        transactions_list = transactions_input.splitlines()

        if not transactions_list:
            return render(request, 'minimize.html', {'error': 'No transactions provided'})

        try:
            transactions, participants = parse_transactions(transactions_list)
            minimized_transactions = minimize_transactions(transactions, participants)
            return render(request, 'minimize.html', {
                'minimized_transactions': minimized_transactions,
                'original_input': transactions_input
            })
        except Exception as e:
            return render(request, 'minimize.html', {
                'error': str(e),
                'original_input': transactions_input
            })

    return render(request, 'minimize.html')

def parse_transactions(transactions_list):
    transactions = []
    participants = set()

    for line in transactions_list:
        parts = line.split()
        if len(parts) != 3:
            raise ValueError("Each transaction must have three values: sender, receiver, amount")
        sender, receiver, amount = parts
        sender = sender.lower()
        receiver = receiver.lower()
        amount = int(amount)
        transactions.append((sender, receiver, amount))
        participants.add(sender)
        participants.add(receiver)

    return transactions, list(participants)

def minimize_transactions(transactions, participants):
    N = len(participants)

    name_to_index = {name: i for i, name in enumerate(participants)}
    index_to_name = {i: name for i, name in enumerate(participants)}

    graph = [[0] * N for _ in range(N)]

    for sender, receiver, amount in transactions:
        graph[name_to_index[sender]][name_to_index[receiver]] += amount

    return run_cash_flow_algorithm(graph, index_to_name)

def run_cash_flow_algorithm(graph, index_to_name):
    N = len(graph)
    
    def getMin(arr):
        minInd = 0
        for i in range(1, N):
            if arr[i] < arr[minInd]:
                minInd = i
        return minInd

    def getMax(arr):
        maxInd = 0
        for i in range(1, N):
            if arr[i] > arr[maxInd]:
                maxInd = i
        return maxInd

    def minOf2(x, y):
        return x if x < y else y

    def minCashFlowRec(amount):
        mxCredit = getMax(amount)
        mxDebit = getMin(amount)

        if amount[mxCredit] == 0 and amount[mxDebit] == 0:
            return []

        min_amount = minOf2(-amount[mxDebit], amount[mxCredit])
        amount[mxCredit] -= min_amount
        amount[mxDebit] += min_amount

        transaction = (index_to_name[mxDebit], index_to_name[mxCredit], min_amount)
        result = [transaction]

        result += minCashFlowRec(amount)
        return result

    def minCashFlow(graph):
        amount = [0] * N
        for p in range(N):
            for i in range(N):
                amount[p] += (graph[i][p] - graph[p][i])
        return minCashFlowRec(amount)

    minimized_transactions = minCashFlow(graph)
    return [f"{debtor} pays {creditor} {amount}" for debtor, creditor, amount in minimized_transactions]
