from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Route, Stop, Vehicle, VehicleStatus, CapacityType, TransportProvider, NearestLandmark, RouteStop
from userauth.models import ProviderRepresentative, CustomUser
from django.core.exceptions import ValidationError

class TransportTest(TestCase):
    def setUp(self):
        """Set up test data for each test method"""
        self.client = Client()
        self.rep_user = get_user_model().objects.create_user(
            email='rep@example.com',
            password='securepassword123',
            name='Rep User',
            contact='03001234567',
            gender='Male',
            is_transporter=True
        )
        self.representative = ProviderRepresentative.objects.create(
            representative_cnic='12345-1234567-1',
            base_user=self.rep_user
        )
        self.provider = TransportProvider.objects.create(
            name='Fast Transit Company',
            representative=self.representative
        )
        self.landmark = NearestLandmark.objects.create(
            landmark_name='FAST University'
        )
        self.start_stop = Stop.objects.create(
            name='FAST University',
            nearest_landmark=self.landmark
        )
        
        self.stop2 = Stop.objects.create(
            name='Gulshan',
            nearest_landmark=self.landmark
        )
        self.route = Route.objects.create(
            route_num=1,
            start_stop=self.start_stop,
            appointed_provider=self.provider
        )
        self.route_stop1 = RouteStop.objects.create(
            route=self.route,
            stop=self.start_stop,
            stop_order=1
        )
        
        self.route_stop2 = RouteStop.objects.create(
            route=self.route,
            stop=self.stop2,
            stop_order=2
        )
        self.status = VehicleStatus.objects.create(
            status_name='Active'
        )
        self.capacity_type = CapacityType.objects.create(
            vehicle_type='Bus',
            max_capacity=30
        )
        self.vehicle = Vehicle.objects.create(
            license_plate='ABC-123',
            allotted_seats=25,
            tracking_id=12345,
            Last_maintenance_date='2023-01-01',
            status=self.status,
            capacity_type=self.capacity_type,
            transport_provider=self.provider,
            route_no=self.route
        )
        self.admin_user = get_user_model().objects.create_user(
            email='admin@example.com',
            password='adminpassword123',
            name='Admin User',
            contact='03001234568',
            gender='Male',
            is_staff=True,
            is_superuser=True
        )

    def test_route_creation(self):
        """Test route creation directly with the model"""

        routes_before = Route.objects.count()
        new_route = Route.objects.create(
            route_num=2,
            start_stop=self.start_stop,
            appointed_provider=self.provider
        )
        self.assertEqual(Route.objects.count(), routes_before + 1)
        self.assertTrue(Route.objects.filter(route_num=2).exists())
    
    def test_vehicle_creation_valid(self):
        """Test vehicle creation with valid data using model directly"""
        vehicles_before = Vehicle.objects.count()
        new_route = Route.objects.create(
            route_num=3,
            start_stop=self.start_stop,
            appointed_provider=self.provider
        )
        new_vehicle = Vehicle.objects.create(
            license_plate='XYZ-789',
            allotted_seats=20,
            tracking_id=67890,
            Last_maintenance_date='2023-01-01',
            status=self.status,
            capacity_type=self.capacity_type,
            transport_provider=self.provider,
            route_no=new_route
        )
        self.assertEqual(Vehicle.objects.count(), vehicles_before + 1)
        self.assertTrue(Vehicle.objects.filter(license_plate='XYZ-789').exists())
    
    def test_vehicle_creation_invalid_license_plate(self):
        """Test vehicle creation with invalid license plate format"""
        invalid_vehicle = Vehicle(
            license_plate='Invalid',
            allotted_seats=20,
            tracking_id=67890,
            Last_maintenance_date='2023-01-01',
            status=self.status,
            capacity_type=self.capacity_type,
            transport_provider=self.provider,
            route_no=self.route
        )
        with self.assertRaises(ValidationError):
            invalid_vehicle.full_clean()
    
    def test_route_stop_order(self):
        """Test route stop ordering"""
        route_stops = self.route.route_stops.all()
        self.assertEqual(route_stops[0].stop, self.start_stop)
        self.assertEqual(route_stops[0].stop_order, 1)
        self.assertEqual(route_stops[1].stop, self.stop2)
        self.assertEqual(route_stops[1].stop_order, 2)
    
    def test_vehicle_model_validation(self):
        """Test vehicle model validation"""
        invalid_vehicle = Vehicle(
            license_plate='Invalid',  # Invalid format
            allotted_seats=20,
            tracking_id=67890,
            Last_maintenance_date='2023-01-01',
            status=self.status,
            capacity_type=self.capacity_type,
            transport_provider=self.provider,
            route_no=self.route
        )
        with self.assertRaises(ValidationError):
            invalid_vehicle.full_clean()
    
    def test_capacity_type_validation(self):
        """Test capacity type validation"""
        invalid_capacity = CapacityType(
            vehicle_type='Large Bus',
            max_capacity=60,
        )
        
        with self.assertRaises(ValidationError):
            invalid_capacity.full_clean()
        valid_capacity = CapacityType(
            vehicle_type='Large Bus',
            max_capacity=45  # Valid
        )
        valid_capacity.save()
        self.assertTrue(CapacityType.objects.filter(vehicle_type='Large Bus').exists())
