from django.db import models
from django.core.validators import RegexValidator,MaxValueValidator
from django.contrib.auth.hashers import make_password
# Create your models here.

class TransportProvider(models.Model):
    name = models.CharField(max_length=100)
    representative = models.OneToOneField('userauth.ProviderRepresentative', 
        on_delete=models.CASCADE,related_name='transport_providers'
    )

    def __str__(self):
        return self.name

class VehicleStatus(models.Model):
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name
    
class CapacityType(models.Model):
    vehicle_type = models.CharField(max_length=50)
    max_capacity = models.IntegerField(validators=[MaxValueValidator(50)])

    def __str__(self):
        return f"{self.vehicle_type} & {self.max_capacity}"

class NearestLandmark(models.Model):
    landmark_name = models.CharField(max_length=100)

    def __str__(self):
        return self.landmark_name

class Stop(models.Model):
    name = models.CharField(max_length=100)
    nearest_landmark = models.ForeignKey(NearestLandmark,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Route(models.Model):
    route_num = models.IntegerField(primary_key=True)
    start_stop = models.ForeignKey(Stop, related_name='start_stop', on_delete=models.CASCADE)
    appointed_provider = models.ForeignKey(TransportProvider, on_delete=models.CASCADE, related_name = 'routes')
    stops = models.ManyToManyField(Stop,through='RouteStop',related_name='stops')

    def __str__(self):
        return f"Route {self.route_num}"
    
class RouteStop(models.Model):
    route = models.ForeignKey(Route,related_name='route_stops',on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_order = models.PositiveIntegerField()

    class Meta:
        unique_together = ('route', 'stop_order')  
        ordering = ['stop_order']  

    def __str__(self):
        return f"Route {self.route.route_num} - Stop {self.stop.name} (Order {self.stop_order})"

class Vehicle(models.Model):
    license_plate= models.CharField(max_length=50,primary_key=True,validators=[
        RegexValidator(
            regex = r'^[A-Z]{3}-\d{3}$',
            message='CNIC must be in the format ABC-123' 
        )
    ],
    default='ABC-123')
    allotted_seats = models.IntegerField()
    tracking_id = models.IntegerField()
    Last_maintenance_date = models.DateField()
    status = models.ForeignKey(VehicleStatus, on_delete=models.SET_NULL, null=True)
    capacity_type = models.ForeignKey(CapacityType, on_delete=models.SET_NULL, null=True)
    transport_provider = models.ForeignKey(TransportProvider, on_delete=models.CASCADE,related_name='vehicles')
    route_no = models.OneToOneField(Route, on_delete=models.CASCADE)

    def __str__(self):
        return self.license_plate




