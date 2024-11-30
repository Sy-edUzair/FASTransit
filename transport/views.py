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
                              "UPDATE userauth_appuser SET assigned_route_id = %s WHERE roll_num = %s",
                              [route_id, request.user.appuser.roll_num]
                              )
                         messages.success(request,f"Route {route_number} assigned to user {request.user.appuser.roll_num}.")
                    else:
                         messages.error(request,f"Route {route_number} not found.")
     else:
          form = RouteForm()
     return render(request, "transport/routes.html",{"providers":providers,"routes": routes,"form":form})

#@login_required(login_url=reverse_lazy("transport:transporter_login"))
#@login_required
def transporter_dashboard(request):
     # Get the logged-in user's transport provider
     user = request.user
     representative = getattr(user, 'providerrepresentative', None)
     
     if not representative:
          return render(request, '403.html', {'error': 'Access denied: You are not a provider representative.'})

     provider_id = representative.transport_providers.id

     with connection.cursor() as cursor:
          # Fetch the total number of vehicles for the transport provider
          cursor.execute("""
               SELECT COUNT(*) 
               FROM transport_vehicle 
               WHERE transport_provider_id = %s
          """, [provider_id])
          total_vehicles = cursor.fetchone()[0]  # Get the first value (total vehicles)

          # Fetch the total number of routes for the transport provider
          cursor.execute("""
               SELECT COUNT(*) 
               FROM transport_route 
               WHERE appointed_provider_id = %s
          """, [provider_id])
          total_routes = cursor.fetchone()[0]  # Get the first value (total routes)

          # Fetch the total number of assigned students or staff for the transport provider
          cursor.execute("""
               SELECT COUNT(*) 
               FROM transport_assigned_staff  -- Replace with the correct table for assigned students/staff
               WHERE transport_provider_id = %s
          """, [provider_id])
          assigned_students_staff = cursor.fetchone()[0]

          # Fetch the list of all drivers with their details (like vehicle, driver name, etc.)
          cursor.execute("""
               SELECT 
               r.route_num,
               v.license_plate AS vehicle_no,
               d.name AS driver_name,
               d.license AS driver_license,
               d.contact_number,
               vs.status_name AS status,
               v.allotted_seats AS capacity,
               v.allotted_seats - v.current_occupancy AS alloted_seats,
               v.Last_maintenance_date AS last_maintenance
               FROM transport_vehicle v
               INNER JOIN transport_route r ON v.route_no_id = r.route_num
               INNER JOIN transport_driver d ON v.driver_id = d.id
               INNER JOIN transport_vehiclestatus vs ON v.status_id = vs.id
               WHERE v.transport_provider_id = %s
          """, [provider_id])
          drivers_data = cursor.fetchall()

     # Organizing the data into a dictionary format to pass to the template
     context = {
          'provider': representative.transport_providers,
          'total_vehicles': total_vehicles,
          'total_routes': total_routes,
          'assigned_students_staff': assigned_students_staff,
          'drivers_data': [
          {
               'route_num': driver[0],
               'vehicle_no': driver[1],
               'driver_name': driver[2],
               'driver_license': driver[3],
               'contact_number': driver[4],
               'status': driver[5],
               'capacity': driver[6],
               'alloted_seats': driver[7],
               'last_maintenance': driver[8],
          } for driver in drivers_data
          ],
     }

     return render(request, "transport/transport-dashboard.html", context)

#@login_required(login_url=reverse_lazy("transport:transporter_login"))
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
     # Query to get all transport providers and their drivers
     raw_query = """
          SELECT tp.id AS provider_id, tp.name AS provider_name, 
               d.id AS driver_id, d.name AS driver_name, 
               d.contact AS driver_contact, d.cnic AS driver_cnic 
          FROM transport_transportprovider tp
          LEFT JOIN transport_driver d ON tp.id = d.appointed_provider_id
     """
    
     # Execute raw query to get providers with their drivers
     with connection.cursor() as cursor:
          cursor.execute(raw_query)
          results = cursor.fetchall()

     # Prepare data for rendering: group drivers by provider
     providers = {}
     for result in results:
          provider_id = result[0]
          provider_name = result[1]
          driver_id = result[2]
          driver_name = result[3]
          driver_contact = result[4]
          driver_cnic = result[5]

          # Add driver under the correct provider
          if provider_id not in providers:
               providers[provider_id] = {
                    "provider_name": provider_name,
                    "drivers": []
               }

          providers[provider_id]["drivers"].append({
               "driver_id": driver_id,
               "driver_name": driver_name,
               "driver_contact": driver_contact,
               "driver_cnic": driver_cnic,
          })

     return render(request, "transport/driver.html", {"providers": providers})

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
     # v.license_number AS vehicle_license_plate,     -- Vehicle license plate
     # r.route_num AS route_number                   -- Route number
     # FROM transport_transportprovider tp
     # INNER JOIN transport_appointed_vehicle v ON tp.vehicle_assigned_id = v.license_plate
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
