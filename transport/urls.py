from django.urls import path
from transport import views

app_name = "transport"

urlpatterns=[  
    path("transport-dashboard/",views.dashboard,name="transport-dashboard"),  
    path("transport-drivers/",views.transport_driver_view,name='transport-drivers'),
    path('view-fees-paid/', views.payment_status_view, name='view_fees_paid'),
    path("add-route/",views.add_route_view,name='add-route'),
    path("transport-logout/",views.logout_view,name="logout"),
    path('add-driver/', views.add_driver, name='add_driver'),
    path('view-routes/', views.view_routes, name='view-routes'),
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),
    path('view-vehicles/', views.view_vehicles, name='view-vehicles'), 
]