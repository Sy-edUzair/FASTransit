from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.conf import settings
from .models import AppUser,CustomUser

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = [
            'roll_num', 'Address', 'cnic',  'emergency_contact', 'department',
        ]
        widgets = {
            'roll_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll Number E.g 22K-4586'}),
            'Address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123 Main Street, Karachi'}),
            'cnic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '13-digit CNIC'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency Contact'}),
            'department': forms.Select(attrs={'class': 'form-select','placeholder': 'Department'}),
        }
        labels = {
            'roll_num': 'Roll Number',
            'cnic': 'CNIC',
            'emergency_contact': 'Emergency Contact',
            'department': 'Department',
        }

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'contact', 'gender', 'profile_image', 'password', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@nu.edu.pk'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'gender': forms.Select(attrs={'class': 'form-select',}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control','placeholder': 'Select Profile image'}),
        }
        labels = {
            'contact': 'Contact Number',
            'gender': 'Gender',
            'profile_image': 'Profile Image',
        }
        

        
class LoginForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'NU Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox(), 
    public_key=settings.RECAPTCHA_PUBLIC_KEY,
    private_key=settings.RECAPTCHA_PRIVATE_KEY,
)