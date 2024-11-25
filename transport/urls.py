from django.urls import path
from transport import views

app_name = "transport"

urlpatterns=[
    path("routes",views.render_route_page, name="render_routes"),    
    path("transporter-login/",views.transporter_login,name="transporter_login"),  
    path("transport-dashboard/",views.transporter_dashboard,name="transport-dashboard"),  
    path("transport-drivers",views.transport_driver_view,name='transport-drivers'),
    path("transport-fees",views.transport_fee_view,name='transport-fees'),
    path("add-route",views.add_route_view,name='add-route'),
    # path("userauth/logout",views.logout_view,name="logout"),  
]