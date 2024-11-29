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
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from .forms import RouteForm

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
               print(email)
               print(password)
     
               try:
                    provider_rep = ProviderRepresentative.objects.get(email__iexact=email)# using email since it is a unique field
                    print(provider_rep)
                    #auth_user = authenticate(request,username=email,password=password)
                    if provider_rep.check_password(password):
                         login(request,provider_rep,backend=None)
                         messages.success(request,"You are logged in")
                         return HttpResponseRedirect(reverse('transport:transport-dashboard'))
                    else:
                         messages.warning(request,"Incorrect Password, Please Try Again!")
                         print("Incorrect Password, Please Try Again!")
               except:
                    messages.warning(request,f"Provider Rep with {email} does not exist")
                    print(f"Provider Rep with {email} does not exist")
     else:
          form = transportLoginForm()
     context={
          'form':form
     }
     return render(request, "transport/transporter-login.html", context)

#@login_required(login_url=reverse_lazy("transport:transporter_login"))
def transporter_dashboard(request):
     print(request.user)
     return render(request, "transport/transport-dashboard.html", {"provider":request.user})

@login_required(login_url=reverse_lazy("transport:transporter_login"))
def render_all_routes(request):
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

     return render(request, "transport/all-routes.html", {"routes": routes})

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
     if request.method == 'POST':
          form = AddRouteForm(request.POST)
          if form.is_valid():
               route_number = form.cleaned_data['route_number']
               num_stops = form.cleaned_data['num_stops']
               stop_names = form.cleaned_data['stops']  # List of stop names

               # Check if the route already exists in the database
               with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM transport_route WHERE route_num = %s", [route_number])
                    existing_route = cursor.fetchone()

                    if existing_route:
                         return HttpResponse("This route number already exists.", status=400)

                    # Insert new route into the database
               try:
                    with connection.cursor() as cursor:
                         cursor.execute("INSERT INTO transport_route (route_num) VALUES (%s)", [route_number])

                    # Fetch the new route ID (You can also get it with Django ORM if needed)
                    with connection.cursor() as cursor:
                         cursor.execute("SELECT id FROM transport_route WHERE route_num = %s", [route_number])
                         route_id = cursor.fetchone()[0]
                    
                         # Add stops to the route
                         for stop_name in stop_names:
                              stop, created = Stop.objects.get_or_create(name=stop_name)
                              cursor.execute(
                              "INSERT INTO transport_routestop (route_id, stop_id) VALUES (%s, %s)",
                              [route_id, stop.id]
                         )

                    return HttpResponse(f"Route {route_number} has been successfully added.")

               except Exception as e:
                    return HttpResponse(f"Error: {str(e)}", status=400)

          else:
               return HttpResponse("Invalid form submission. Please check the data.", status=400)

     else:
          form = AddRouteForm()

     return render(request, 'transport/add-route.html', {'form': form})



def transport_driver_view(request):
     # search_route = request.GET.get('search_route', '')
     # search_vehicle = request.GET.get('search_vehicle', '')
     # search_phone = request.GET.get('search_phone', '')

     # raw_query = """
     # SELECT 
     # tp.id AS provider_id,                         -- TransportProvider ID
     # tp.name AS provider_name,                     -- TransportProvider name
     # v.license_plate AS vehicle_license_plate,     -- Vehicle license plate
     # r.route_num AS route_number                   -- Route number
     # FROM transport_transportprovider tp
     # INNER JOIN transport_vehicle v ON tp.vehicle_assigned_id = v.license_plate
     # INNER JOIN transport_route r ON r.appointed_provider_id = tp.id
     # WHERE 1=1;

     # """

     # # Append filters only if search parameters are provided
     # if search_route or search_vehicle or search_phone:
     #      if search_route:
     #           raw_query += f" AND r.route_num LIKE '%{search_route}%'"
     #      if search_vehicle:
     #           raw_query += f" AND v.registration_number LIKE '%{search_vehicle}%'"
     #      if search_phone:
     #           raw_query += f" AND tp.driver_contact_number LIKE '%{search_phone}%'"
     # else:
     #      raw_query += " LIMIT 50"

     # with connection.cursor() as cursor:
     #      cursor.execute(raw_query)
     #      rows = cursor.fetchall()

     
     # columns = ['provider_id', 'provider_name', 'driver_license', 'contact_number', 'vehicle_no', 'route_name']
     # providers = [dict(zip(columns, row)) for row in rows]

     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "transport/driver.html", {"providers": providers})

def tracking_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "transport/tracking.html",{"providers":providers})
