from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Store, Product, Employee, UserProfile, WorkDate
from .models import TransactionRequest

class TransactionRequestForm(forms.ModelForm):
    class Meta:
        model = TransactionRequest
        fields = ['store', 'product', 'quantity']
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'work_date', 'capacity', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'model', 'store', 'serial_number', 'produced_date', 'photo', 'price', 'description', 'category', 'quantity', 'manufacturer']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'role', 'store','user', 'profile_photo']
class WorkDateForm(forms.Form):
    work_dates = forms.ModelMultipleChoiceField(
        queryset=WorkDate.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )