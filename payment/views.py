from django.shortcuts import render,redirect
from django.conf import settings
from decimal import Decimal
from transport.models import *

# Create your views here.
def voucher_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "payment/voucher.html",{"providers":providers})
