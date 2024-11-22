from django.urls import path
from transport import views

app_name = "transport"

urlpatterns=[
    path("routes",views.render_route_page, name="render_routes"),    
    path("transporter-login/",views.transporter_login,name="transporter_login"),  
     path("transporter-dashboard/",views.transporter_dashboard,name="transport-dashboard"),  
    # path("userauth/logout",views.logout_view,name="logout"),  
]