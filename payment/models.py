from django.db import models
from userauth.models import User

# Create your models here.

class Receipt(models.Model):
    receipt_number = models.CharField(max_length=50)
    voucher_number = models.CharField(max_length=50)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    receipt = models.ForeignKey(Receipt, on_delete=models.SET_NULL, null=True)

class PaymentMethod(models.Model):
    method_name = models.CharField(max_length=50)

    def __str__(self):
        return self.method_name
