from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.conf import settings
from driver.models import Driver
from transport.models import Stop,Route,RouteStop,Vehicle

class transportLoginForm(forms.Form):
    email=forms.CharField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Provider Email'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',"placeholder":"Password"}))
    captcha=ReCaptchaField(widget=ReCaptchaV2Checkbox(), public_key=settings.RECAPTCHA_PUBLIC_KEY,private_key=settings.RECAPTCHA_PRIVATE_KEY,)
    
class RouteForm(forms.Form):
    route_num = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Route Number'}),
        label="Route Number"
    )
    
    start_stop = forms.ModelChoiceField(
        queryset=Stop.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Start Stop"
    )
    
    # Multiple selection dropdown to choose stops from existing ones
    stops = forms.ModelMultipleChoiceField(
        queryset=Stop.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Select Stops"
    )
    
    stop_orders = forms.CharField(widget=forms.HiddenInput, required=False)
    
    def clean_route_num(self):
        route_num = self.cleaned_data.get('route_num')
        if Route.objects.filter(route_num=route_num).exists():
            raise forms.ValidationError("Route number already exists.")
        return route_num
    
    
    
    
class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['name', 'cnic', 'contact', 'license_number', 'appointed_vehicle']

        widgets = {
            'appointed_vehicle': forms.Select(),
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['license_plate', 'allotted_seats', 'tracking_id', 'Last_maintenance_date',  # Use exact field name
                  'status', 'capacity_type', 'route_no']
        widgets = {
            'Last_maintenance_date': forms.DateInput(attrs={'type': 'date'})  # Update this as well
        }

class SelectRouteForm(forms.Form):
    route_number = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={
            'id': 'routeInput',
            'class': 'route-select-input',
            'placeholder': 'Enter Route Number (e.g., 1)'
        })
    )
    
    
class SelectStopForm(forms.Form):
    start_stop = forms.ModelChoiceField(queryset=Stop.objects.all(), label="Select Stop")
    
    def __init__(self, *args, **kwargs):
        selected_route = kwargs.pop('selected_route', None)  # Extract the selected route
        super().__init__(*args, **kwargs)

        if selected_route:
            self.fields['start_stop'].queryset = Stop.objects.filter(
                id__in=RouteStop.objects.filter(route_id=selected_route).values('stop_id')
            ).distinct()