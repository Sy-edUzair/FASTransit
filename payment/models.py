from django.db import models
from django.utils.timezone import now
from userauth.models import AppUser

# Create your models here.
class PaymentStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name

class Voucher(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="vouchers")
    semester=models.CharField(max_length=100)
    status = models.ForeignKey(PaymentStatus, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(default=30000)
    due_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_active(self):
        """
        Determines if the voucher is active based on its status and expiry_date.
        """
        if self.status.status_name == 'Succeeded':
            return False
        if self.due_date and now() > self.due_date:
            return False
        return True
    
class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    profile_voucher_number = models.CharField(max_length=255)
    browser_view = models.URLField()

    def __str__(self):
        return f"Receipt {self.receipt_id}"

class PaymentMethod(models.Model):  
    method_id = models.AutoField(primary_key=True)
    method_name = models.CharField(max_length=100)

    def __str__(self):
        return self.method_name
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    voucher = models.OneToOneField(Voucher,on_delete=models.CASCADE, related_name="vouchers")
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="payments")
    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE, related_name="payment")
    method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name="payments")
    amount = models.IntegerField(default=30000)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.voucher.status.status_name}"

