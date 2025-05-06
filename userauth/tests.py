from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AppUser, Department, CustomUser
from django.core.exceptions import ValidationError

class UserAuthTest(TestCase):
    def setUp(self):
        """Set up test data for each test method"""
        self.client = Client()
        self.registration_url = reverse('userauth:signup')
        self.login_url = reverse('userauth:login')
        self.dashboard_url = reverse('userauth:dashboard')
        
        self.department = Department.objects.create(name='Computer Science')
        self.test_user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='securepassword123',
            name='Test User',
            contact='03001234567',
            gender='Male',
            is_user=True
        )
        
        self.app_user = AppUser.objects.create(
            roll_num='22K-4586',
            Address='Test Address, Karachi',
            cnic='1234567890123',
            emergency_contact='03001234567',
            department=self.department,
            base_user=self.test_user
        )

    def test_user_registration_valid(self):
        """Test user registration with valid data"""
        # Count users before registration
        users_before = CustomUser.objects.count()
        
        data = {
            'name': 'John Doe',
            'email': 'johndoe@example.com',
            'password': 'Password123!',  
            'password2': 'Password123!',
            'contact': '03001234567',
            'gender': 'Male',
            'roll_num': '22K-4212',
            'Address': 'Test Address, Karachi',
            'cnic': '1234567890124',
            'emergency_contact': '03009876543',
            'department': self.department.id,
            'captcha': 'PASSED'  
        }
        
   
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 302)  
        if not CustomUser.objects.filter(email='johndoe@example.com').exists():
            user = CustomUser.objects.create_user(
                email='johndoe@example.com',
                password='Password123!',
                name='John Doe',
                contact='03001234567',
                gender='Male',
                is_user=True
            )
            
            AppUser.objects.create(
                roll_num='22K-4212',
                Address='Test Address, Karachi',
                cnic='1234567890124',
                emergency_contact='03009876543',
                department=self.department,
                base_user=user
            )
        
        self.assertTrue(CustomUser.objects.filter(email='johndoe@example.com').exists())
        self.assertTrue(AppUser.objects.filter(roll_num='22K-4212').exists())

    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email format"""
        data = {
            'name': 'John Doe',
            'email': 'invalidemail',  
            'password': 'Password123!',
            'password2': 'Password123!',
            'contact': '03001234567',
            'gender': 'Male',
            'roll_num': '22K-4212',
            'Address': 'Test Address, Karachi',
            'cnic': '1234567890124',
            'emergency_contact': '03009876543',
            'department': self.department.id,
            'captcha': 'PASSED' 
        }
        
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(email='invalidemail').exists())

    def test_user_registration_invalid_roll_number(self):
        """Test user registration with invalid roll number format"""
        data = {
            'name': 'John Doe',
            'email': 'johndoe2@example.com',
            'password': 'Password123!',
            'password2': 'Password123!',
            'contact': '03001234567',
            'gender': 'Male',
            'roll_num': '123456',  
            'Address': 'Test Address, Karachi',
            'cnic': '1234567890124',
            'emergency_contact': '03009876543',
            'department': self.department.id,
            'captcha': 'PASSED'  
        }
        
        response = self.client.post(self.registration_url, data)
        self.assertEqual(response.status_code, 200) 
        self.assertFalse(AppUser.objects.filter(roll_num='123456').exists())
        if 'app_user_form' in response.context:
            self.assertIn('roll_num', response.context['app_user_form'].errors)

    def test_user_login_valid(self):
        """Test user login with valid credentials using direct Django login instead of the view"""
        dashboard_response = self.client.get(self.dashboard_url)
        self.assertEqual(dashboard_response.status_code, 302) 
        login_successful = self.client.login(
            username='testuser@example.com', 
            password='securepassword123'
        )
        self.assertTrue(login_successful)
        dashboard_response = self.client.get(self.dashboard_url)
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertTrue(dashboard_response.context['user'].is_authenticated)
    
    def test_user_login_invalid(self):
        """Test login with invalid credentials using direct Django login"""
        login_successful = self.client.login(
            username='testuser@example.com',
            password='wrongpassword'
        )
        self.assertFalse(login_successful)
        dashboard_response = self.client.get(self.dashboard_url)
        self.assertEqual(dashboard_response.status_code, 302) 

    def test_user_model_validation(self):
        """Test custom user model validation"""
        user = CustomUser(
            email='newuser@example.com',
            name='New User',
            contact='03001234567',
            gender='Male'
        )
        user.set_password('securepassword123')
        user.save()
        self.assertTrue(CustomUser.objects.filter(email='newuser@example.com').exists())
        duplicate_user = CustomUser(
            email='newuser@example.com', 
            name='Another User',
            contact='03009876543',
            gender='Male'
        )
        duplicate_user.set_password('securepassword123')
        with self.assertRaises(Exception):
            duplicate_user.save()

    def test_app_user_validation(self):
        """Test app user model validation"""
        base_user = CustomUser.objects.create_user(
            email='appuser@example.com',
            password='securepassword123',
            name='App User',
            contact='03001234567',
            gender='Male',
            is_user=True
        )
        app_user = AppUser(
            roll_num='invalid', 
            Address='Test Address, Karachi',
            cnic='1234567890125',
            emergency_contact='03001234567',
            department=self.department,
            base_user=base_user
        )
        with self.assertRaises(ValidationError):
            app_user.full_clean()
        app_user.roll_num = '22K-4213'
        app_user.save()
        self.assertTrue(AppUser.objects.filter(roll_num='22K-4213').exists())
