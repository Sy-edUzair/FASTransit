from django.urls import path
from payment import views

app_name = "payment"

urlpatterns=[
    path("voucher/",views.voucher_view,name='voucher'),
    path("payment-history/",views.payment_history_view,name='payment-history'),
    ]