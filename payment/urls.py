from django.urls import path
from payment import views

app_name = "payment"

urlpatterns=[
    path("voucher/",views.voucher_view,name='voucher'),
]