from django.urls import path
from driver import views

app_name = "driver"

urlpatterns=[
    path("driver-detail",views.driver_detail_view,name='driver-detail'),
    # path("userauth/logout",views.logout_view,name="logout"),  
]