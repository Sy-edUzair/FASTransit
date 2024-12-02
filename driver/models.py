from django.db import models
from django.core.validators import RegexValidator
from transport.models import TransportProvider,Vehicle

# Create your models here.
class DriverStatus(models.Model):
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name

class Driver(models.Model):
    cnic_validator = RegexValidator(
        regex=r'^\d{5}-\d{7}-\d{1}$', 
        message='CNIC must be in the format XXXX-XXXXXXX-X'
    )
    cnic = models.CharField(
        max_length=15,
        primary_key=True,
        validators = [cnic_validator]
    )
    name = models.CharField(max_length=25)
    contact = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50)
    registration_status = models.ForeignKey(DriverStatus, on_delete=models.SET_NULL, null=True)
    appointed_provider = models.ForeignKey(TransportProvider, on_delete=models.CASCADE, related_name = 'drivers')
    appointed_vehicle = models.OneToOneField(Vehicle, on_delete = models.CASCADE)

    def __str__(self):
        return f'({self.name})'

