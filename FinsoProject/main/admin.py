from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, ExpenseCategory

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_date')

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ('user', 'phone_no', 'address', 'state', 'zip_code', 'profile_image', 'basic_income', 'created_date')