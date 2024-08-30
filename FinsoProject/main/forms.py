from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    phone_no = forms.CharField(max_length=15)
    address = forms.CharField(max_length=255)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    profile_image = forms.ImageField(required=False)
    basic_income = forms.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_no', 'address', 'state', 'zip_code', 'profile_image', 'basic_income')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        profile = UserProfile.objects.create(
            user=user,
            phone_no=self.cleaned_data['phone_no'],
            address=self.cleaned_data['address'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            profile_image=self.cleaned_data['profile_image'],
            basic_income=self.cleaned_data['basic_income']
        )
        return user
