from django.urls import path
from payment import views

app_name = "payment"

urlpatterns=[
    path("voucher/",views.voucher_view,name='voucher'),
    path("payment-history/",views.payment_history_view,name='payment-history'),
    #path('generate-challan/', views.generate_challan_pdf, name='generate_challan_pdf'),
    path("create-checkout-session",views.CreateCheckoutSessionView.as_view(),name='create-checkout-session'),
    path('cancel/',views.CancelView.as_view(),name="cancel"),
    path('success/',views.SuccessView.as_view(),name="success"),
    path('webhook/',views.webhook_view,name='stripe_webhook'),
]