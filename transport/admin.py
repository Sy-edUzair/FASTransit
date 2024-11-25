from django.contrib import admin
from .models import *


# Register your models here.

class ProviderRepAdmin(admin.ModelAdmin):
    list_display =['representative_name' , 'representative_cnic', 'representative_contact']
    search_fields = ['representative_name', 'representative_cnic']
    list_per_page = 20

class TransportProviderAdmin(admin.ModelAdmin):
    list_display=['name','representative']
    search_fields = ['name']
    list_per_page = 20

class StatusAdmin(admin.ModelAdmin):
    list_display = ['status_name']
    search_fields = ['status_name']

class CapacityTypeAdmin(admin.ModelAdmin):
    list_display=['vehicle_type','max_capacity']
    search_fields = ['vehicle_type']

class LandmarkAdmin(admin.ModelAdmin):
    list_display=['landmark_name']
    search_fields = ['landmark_name']

class StopAdmin(admin.ModelAdmin):
    list_display=['name','nearest_landmark']


class RouteStopInline(admin.TabularInline):
    model = RouteStop
    extra = 1  # Number of extra blank rows to display
    fields = ('stop', 'stop_order')
    ordering = ['stop_order']

class RouteAdmin(admin.ModelAdmin):
   list_display = ['route_num', 'start_stop', 'end_stop', 'appointed_provider']
   inlines = [RouteStopInline]  

class VehicleAdmin(admin.ModelAdmin):
    list_display = ['license_plate', 'allotted_seats', 'tracking_id', 'Last_maintenance_date', 'status', 'transport_provider', 'route_no']
    search_fields = ['license_plate', 'tracking_id', 'status', 'transport_provider', 'route_no']
    list_filter = ['status', 'transport_provider']
    date_hierarchy = 'Last_maintenance_date'


admin.site.register(ProviderRepresentative,ProviderRepAdmin)
admin.site.register(TransportProvider,TransportProviderAdmin)
admin.site.register(VehicleStatus,StatusAdmin)
admin.site.register(CapacityType,CapacityTypeAdmin)
admin.site.register(NearestLandmark,LandmarkAdmin)
admin.site.register(Stop,StopAdmin)
admin.site.register(Route,RouteAdmin)
admin.site.register(Vehicle,VehicleAdmin)












