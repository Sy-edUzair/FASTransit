from django.contrib import admin
from .models import *
from .forms import *


# # Custom action to generate vouchers for all users based on semester input
# def generate_vouchers_for_all_users(modeladmin, request, queryset):
#     if 'apply' in request.POST:
#         # Get the semester from the form data
#         form = GenerateVoucherForm(request.POST)
#         if form.is_valid():
#             semester = form.cleaned_data['semester']
#             # Fetch all users
#             users = AppUser.objects.all()
#             payment_status = PaymentStatus.objects.get_or_create(status_name="Pending")

    
#             for user in users:
#                 existing_voucher = Voucher.objects.filter(user=user, semester=semester, status__status_name="Pending").exists()
#                 if not existing_voucher:
#                     Voucher.objects.create(
#                         user=user,
#                         semester=semester,  
#                         status=payment_status,
#                         amount=39000,  
#                         due_date=now(),
#                     )

#             # Return a success message
#             modeladmin.message_user(request, f"Vouchers for semester '{semester}' have been generated for all users.")
#     else:
#         form = GenerateVoucherForm()
#     context = {
#         'form': form,
#         'action': 'generate_vouchers_for_all_users'
#     }
#     return modeladmin.render_change_form(request, context)


# Customizing the admin for Voucher
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('user', 'semester', 'status', 'amount', 'due_date', 'created_at', 'updated_at')
    #actions = [generate_vouchers_for_all_users]  # Adding the custom action to the admin

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     # Add custom action
    #     actions['generate_vouchers_for_all_users'] = (generate_vouchers_for_all_users, 'generate_vouchers_for_all_users', 'Generate vouchers for all users')
    #     return actions

    # def save_model(self, request, obj, form, change):
    #     super().save_model(request, obj, form, change)

    # def is_active(self, obj):
    #     return obj.is_active
    # is_active.boolean = True

    # Optional: Customizing the display of the is_active field
    list_filter = ('status', 'semester')



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
    list_display = ['payment_id', 'user', 'receipt', 'method','amount', 'date']
    search_fields = ['user__username', 'receipt__profile_voucher_number'] 
    list_filter = [ 'method', 'date'] 

admin.site.register(Receipt,ReceiptAdmin)
admin.site.register(Voucher,VoucherAdmin)
admin.site.register(PaymentMethod,PaymentMethodAdmin)
admin.site.register(PaymentStatus,PaymentStatusAdmin)
admin.site.register(Payment,PaymentAdmin)