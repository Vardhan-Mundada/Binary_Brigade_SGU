from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    basic_income = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.username
    

class ExpenseCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    name = models.CharField(max_length=100)  
    created_date = models.DateTimeField(auto_now_add=True)  
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, default=True, null=False )

    def __str__(self):
        return self.name
    

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, default='Miscellaneous')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type=models.CharField(max_length=100) #income, expense, investment
    notes = models.TextField(default='Transaction')
    transaction_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.amount)
    

class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Income of {self.user.username}: {self.amount}"
    

class RecurringExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=50)  # e.g., daily, weekly, monthly
    start_date = models.DateField(default=timezone.now)
    next_due_date = models.DateField()

    def __str__(self):
        return self.name