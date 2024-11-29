from django.db import models
from userauth.models import AppUser

# Create your models here.

class Receipt(models.Model):
    receipt_id = models.AutoField(primary_key=True)
    profile_voucher_number = models.CharField(max_length=255)

    def __str__(self):
        return f"Receipt {self.receipt_id}"

class PaymentMethod(models.Model):  
    method_id = models.AutoField(primary_key=True)
    method_name = models.CharField(max_length=100)

    def __str__(self):
        return self.method_name
    
class PaymentStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name="payments")
    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE, related_name="payment")
    method = models.OneToOneField(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name="payments")
    status = models.OneToOneField(PaymentStatus, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"

