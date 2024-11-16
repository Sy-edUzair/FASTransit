from django.contrib import admin
from .models import *

class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'cnic', 'contact', 'license_number', 'appointed_provider', 'appointed_vehicle', 'registration_status']
    search_fields = ['name', 'cnic', 'license_number']
    list_filter = ['registration_status', 'appointed_provider']
    ordering = ['name',]


class DriverStatusAdmin(admin.ModelAdmin):
    list_display = ['status_name',]
    search_fields = ['status_name',]


admin.site.register(Driver,DriverAdmin)
admin.site.register(DriverStatus,DriverStatusAdmin)