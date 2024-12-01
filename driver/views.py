from django.shortcuts import render
from django.db import connection
from .models import *
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse,reverse_lazy
from datetime import datetime
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
#from .forms import *
from .models import *
from transport.models import *
from noticeboard.models import *
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
#from .forms import RouteForm
# Create your views here.

def driver_detail_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     route_id = request.user.appuser.assigned_route.route_num
     vehicle = Vehicle.objects.get(route_no=route_id)
     driver=Driver.objects.get(appointed_vehicle=vehicle.license_plate)
     return render(request, "driver/driver-detail.html",{"providers":providers,'user':request.user,'vehicle':vehicle,'driver':driver})

def modify_driver_detail_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "driver/modify-driver.html",{"providers":providers})