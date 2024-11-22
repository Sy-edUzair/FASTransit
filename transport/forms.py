from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.conf import settings
from .models import ProviderRepresentative

class transportLoginForm(forms.Form):
    email=forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Provider Email'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    captcha=ReCaptchaField(widget=ReCaptchaV2Checkbox(), public_key=settings.RECAPTCHA_PUBLIC_KEY,private_key=settings.RECAPTCHA_PRIVATE_KEY,)