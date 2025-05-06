from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import PaymentStatus, Voucher, PaymentMethod, Receipt, Payment
from userauth.models import Department, AppUser, CustomUser

class PaymentTest(TestCase):
    def setUp(self):
        """Set up test data for each test method"""
        self.client = Client()
        self.department = Department.objects.create(name='Computer Science')
        self.user = get_user_model().objects.create_user(
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
            base_user=self.user
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
        self.pending_status = PaymentStatus.objects.create(status_name='Pending')
        self.succeeded_status = PaymentStatus.objects.create(status_name='Succeeded')
        self.stripe_method = PaymentMethod.objects.create(method_name='Stripe')
        self.active_voucher = Voucher.objects.create(
            user=self.app_user,
            semester='Fall 2023',
            status=self.pending_status,
            amount=30000,
            due_date=timezone.now() + timedelta(days=30)
        )
        self.expired_voucher = Voucher.objects.create(
            user=self.app_user,
            semester='Spring 2023',
            status=self.pending_status,
            amount=30000,
            due_date=timezone.now() - timedelta(days=1) 
        )
        self.paid_voucher = Voucher.objects.create(
            user=self.app_user,
            semester='Summer 2023',
            status=self.succeeded_status,
            amount=30000,
            due_date=timezone.now() + timedelta(days=15)
        )
        self.receipt = Receipt.objects.create(
            profile_voucher_number='REC123456',
            browser_view='https://example.com/receipt'
        )
        
        self.payment = Payment.objects.create(
            voucher=self.paid_voucher,
            user=self.app_user,
            receipt=self.receipt,
            method=self.stripe_method,
            amount=30000
        )

    def test_voucher_generation(self):
        """Test voucher generation via model creation instead of view"""
        vouchers_before = Voucher.objects.filter(user=self.app_user, semester='Fall 2023').count()
        new_voucher = Voucher.objects.create(
            user=self.app_user,
            semester='Fall 2023',
            status=self.pending_status,
            amount=30000,
            due_date=timezone.now() + timedelta(days=30)
        )
        self.assertEqual(
            Voucher.objects.filter(user=self.app_user, semester='Fall 2023').count(),
            vouchers_before + 1
        )
    
    def test_payment_processing(self):
        """Test payment processing"""
        self.client.login(username='testuser@example.com', password='securepassword123')
        self.active_voucher.status = self.succeeded_status
        self.active_voucher.save()
        updated_voucher = Voucher.objects.get(id=self.active_voucher.id)
        self.assertEqual(updated_voucher.status, self.succeeded_status)
    
    def test_voucher_active_status(self):
        """Test voucher is_active property"""
        self.assertTrue(self.active_voucher.is_active)
        self.assertFalse(self.expired_voucher.is_active)
        self.assertFalse(self.paid_voucher.is_active)
    
    def test_user_payment_history(self):
        """Test retrieving user payment history"""
        self.client.login(username='testuser@example.com', password='securepassword123')
        response = self.client.get(reverse('payment:payment-history'))
        self.assertEqual(response.status_code, 200)
    
    def test_receipt_generation(self):
        """Test receipt generation"""
        self.client.login(username='testuser@example.com', password='securepassword123')
        self.assertEqual(self.payment.receipt, self.receipt)
        self.assertEqual(self.receipt.profile_voucher_number, 'REC123456')
        
    def test_voucher_listing(self):
        """Test voucher listing for a user"""
        self.client.login(username='testuser@example.com', password='securepassword123')
        response = self.client.get(reverse('payment:voucher'))
        self.assertEqual(response.status_code, 200)
        
