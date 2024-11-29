from django.urls import path
from driver import views

app_name = "driver"

urlpatterns=[
    path("driver-detail/",views.driver_detail_view,name='driver-detail'),
    path("modify-driver/",views.modify_driver_detail_view,name='modify-driver'),
    # path("userauth/logout",views.logout_view,name="logout"),  
]