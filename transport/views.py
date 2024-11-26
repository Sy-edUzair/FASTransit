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
from .forms import *
from .models import *
from transport.models import *
from noticeboard.models import *

@login_required(login_url=settings.LOGIN_URL)
def render_route_page(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     raw_query_2= """
          SELECT r.route_num AS route_num, s.id AS stop_id, s.name AS stop_name FROM transport_route AS r JOIN transport_routestop AS rs ON r.route_num = rs.route_id JOIN transport_stop AS s ON rs.stop_id = s.id ORDER BY r.route_num, rs.stop_order;
     """

     # Execute the raw query
     with connection.cursor() as cursor:
          cursor.execute(raw_query_2)
          results = cursor.fetchall()

     # Organize results into a structure suitable for the template
     routes = {}
     for route_num, stop_id, stop_name in results:
          if route_num not in routes:
               idx=0
               routes[route_num] = {"stops": []}
          if stop_id:
               idx+=1
               routes[route_num]["stops"].append({"idx":idx,"id": stop_id, "name": stop_name})

     if request.method == 'POST':
          form = RouteForm(request.POST)
          if form.is_valid():
               route_number = form.cleaned_data['route_number']
               print(route_number)
               with connection.cursor() as cursor:
               # Fetch the specific route
                    cursor.execute("SELECT route_num FROM transport_route WHERE route_num = %s", [route_number])
                    route = cursor.fetchone()
                    if route:
                         route_id = route[0]

                         # Assign the route to the user
                         cursor.execute(
                              "UPDATE userauth_user SET assigned_route_id = %s WHERE roll_num = %s",
                              [route_id, request.user.roll_num]
                              )
                         messages.success(request,f"Route {route_number} assigned to user {request.user.roll_num}.")
                    else:
                         messages.error(request,f"Route {route_number} not found.")
     else:
          form = RouteForm()
     return render(request, "transport/routes.html",{"providers":providers,"routes": routes,"form":form})

@csrf_protect
def transporter_login(request):
    # raw_query = """
    #     SELECT *
    #     FROM noticeboard_notice
    #     WHERE is_active = TRUE 
    #     ORDER BY date_posted DESC
    # """
    # notices = Notice.objects.raw(raw_query)
     if request.method=="POST":
          form = transportLoginForm(request.POST)
          if form.is_valid():
               email = form.cleaned_data['email']
               password = form.cleaned_data['password']
          
               try:
                    provider_rep = ProviderRepresentative.objects.get(email__iexact=email)# using email since it is a unique field
                    auth_user = authenticate(request,username=email,password=password)
          
                    if auth_user is not None:
                         login(request,auth_user)
                         messages.success(request,"You are logged in")
                         return HttpResponseRedirect(reverse('userauth:dashboard'))
                    else:
                         messages.warning(request,"Incorrect Password, Please Try Again!")
                         print("Incorrect Password, Please Try Again!")
               except:
                    messages.warning(request,f"User with {email} does not exist")
                    print(f"User with {email} does not exist")
     else:
          form = transportLoginForm()
     context={
          'form':form
     }
     return render(request, "transport/transporter-login.html", context)

@login_required(login_url=reverse_lazy("transport:transporter_login"))
def transporter_dashboard(request):
    # raw_query = """
    #     SELECT *
    #     FROM noticeboard_notice
    #     WHERE is_active = TRUE 
    #     ORDER BY date_posted DESC
    # """
    # notices = Notice.objects.raw(raw_query)
     return render(request, "transport/transport-dashboard.html", {})

@csrf_protect
def logout_view(request):
     logout(request)
     messages.success(request,"You logged out")
     return HttpResponseRedirect(reverse("transport:transporter_login"))

def transport_driver_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "transport/driver.html",{"providers":providers})

def transport_fee_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "transport/fee-collection.html",{"providers":providers})

def add_route_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "add-route.html",{"providers":providers})
def driver_detail_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "driver-detail.html",{"providers":providers})