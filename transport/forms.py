from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.conf import settings
from .models import ProviderRepresentative

class transportLoginForm(forms.Form):
    email=forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Provider Email'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    captcha=ReCaptchaField(widget=ReCaptchaV2Checkbox(), public_key=settings.RECAPTCHA_PUBLIC_KEY,private_key=settings.RECAPTCHA_PRIVATE_KEY,)

class RouteForm(forms.Form):
    route_number = forms.CharField(
        label="Route Number",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Route Number'
        })
    )
    
    num_stops = forms.IntegerField(
        label="Number of Stops",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'id': 'numStops',
            'class': 'form-control',
            'placeholder': 'Enter Number of Stops',
            'oninput': 'generateStopFields()'
        })
    )
    
    # Dynamically generated fields will be added as stop fields in the view.
    # This will be populated with the actual stop names.
    stops = forms.CharField(
        required=False,  # This field will be populated dynamically
        widget=forms.HiddenInput()  # Hidden field to hold the stops
    )
    
    def clean_stops(self):
        # This will clean and process the dynamically generated stop fields
        stops = self.cleaned_data['stops']
        # Convert the stops from string to list if needed (e.g., 'Stop 1, Stop 2')
        stop_list = stops.split(",")  # Assuming stops are separated by commas
        return stop_list

class TransportFeeForm(forms.Form):
    # provider = forms.ModelChoiceField(queryset=TransportProvider.objects.all(), label="Transport Provider", empty_label="Select a Provider")
    fee = forms.DecimalField(max_digits=10, decimal_places=2, label="Fee Amount", widget=forms.NumberInput(attrs={'class': 'form-control'}))