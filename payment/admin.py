from django.contrib import admin
from .models import *


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_id', 'profile_voucher_number']  
    search_fields = ['profile_voucher_number']  


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['method_id', 'method_name']  
    search_fields = ['method_name'] 


class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['status_id', 'status_name'] 
    search_fields = ['status_name']  


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'receipt', 'method', 'status', 'amount', 'date']
    search_fields = ['user__username', 'receipt__profile_voucher_number'] 
    list_filter = ['status', 'method', 'date'] 

admin.site.register(Receipt,ReceiptAdmin)
admin.site.register(PaymentMethod,PaymentMethodAdmin)
admin.site.register(PaymentStatus,PaymentStatusAdmin)
admin.site.register(Payment,PaymentAdmin)