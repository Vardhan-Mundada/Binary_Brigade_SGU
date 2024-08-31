from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('', views.home, name='home'),
    path('analytics/', views.analytics, name='analytics'),
    path('login/', views.login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('send-otp-email/', views.send_otp_email, name='send_otp_email'),
    path('send-otp-mobile/', views.send_otp_mobile, name='send_otp_mobile'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_income/', views.add_income, name='add_income'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('categories/', views.category_list, name='category_list'),
    path('add_categories/', views.add_category, name='add_category'),
    path('addall/', views.addall, name='addall'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export_report/', views.export_report, name='export_report'),
    path('update-transactions/', views.update_transaction_category, name='update_transaction_category'),
    path('transactions-for-past-days/', views.transactions_for_past_days, name='transactions_for_past_days'),
    # path('expense-statistics/', views.expense_statistics, name='expense_statistics'),
    path('add_stock/', views.add_stock, name='add_stock'),
    path('add_mutual_fund/', views.add_mutual_fund, name='add_mutual_fund'),
    path('add_fixed_deposit/', views.add_fixed_deposit, name='add_fixed_deposit'),
    path('dashboard/', views.dashboard, name='dashboard'),


]