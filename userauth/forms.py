from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.conf import settings
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Confirm Password"}))
    class Meta:
        model = User
        fields = [
            'roll_num', 'email', 'name', 'Address', 'cnic', 
            'contact', 'emergency_contact', 'gender', 
            'profile_image', 'department',
        ]
        widgets = {
            'roll_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number E.g 22K-4586'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@nu.edu.pk'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'Address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main Street, Karachi'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '13-digit CNIC'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select','placeholder': 'Department'}),
        }
        labels = {
            'roll_num': 'Roll Number',
            'cnic': 'CNIC',
            'contact': 'Contact Number',
            'emergency_contact': 'Emergency Contact',
            'gender': 'Gender',
            'profile_image': 'Profile Image',
            'department': 'Department',
        }

class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'NU Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(), 
    public_key=settings.RECAPTCHA_PUBLIC_KEY,
    private_key=settings.RECAPTCHA_PRIVATE_KEY,
    )