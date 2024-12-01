from django.shortcuts import render
from django.db import connection
from .models import *
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse,reverse_lazy
from datetime import datetime
from django.db import connection
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from .forms import *
from .models import *
from transport.models import *
from userauth.models import AppUser  # Add Payment model here
from payment.models import Payment,PaymentStatus
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
def transporter_dashboard(request):
     # Get the logged-in user's transport provider
     user = request.user
     representative = getattr(user, 'providerrepresentative', None)
     
     if not representative:
          return HttpResponseForbidden("Access denied: You are not a provider representative.")

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
     # Get search filters from the request
     search_id = request.GET.get('search_id', '').strip()
     search_name = request.GET.get('search_name', '').strip()
     search_phone = request.GET.get('search_phone', '').strip()

     # Define the raw SQL query with conditions based on search filters
     query = """
         SELECT 
    base_user.name AS student_name,
    base_user.gender,
    appuser.roll_num,            -- Assuming 'roll_num' is a column in the appuser table
    payment.amount,              -- Selecting the amount directly without SUM
    payment_status.status_name AS payment_status,
    base_user.contact AS phone,
    base_user.email
FROM userauth_appuser AS appuser
JOIN userauth_customuser AS base_user ON appuser.base_user_id = base_user.id
LEFT JOIN transport_route AS route ON appuser.assigned_route_id = route.route_num
LEFT JOIN userauth_department AS department ON appuser.department_id = department.id
LEFT JOIN payment_payment AS payment ON appuser.base_user_id = payment.user_id
LEFT JOIN payment_paymentstatus AS payment_status ON payment.status_id = payment_status.status_id;


     """

     # Add filtering conditions based on the search query
     if search_id:
          query += " AND appuser.roll_num LIKE %s"
     if search_name:
          query += " AND base_user.name LIKE %s"
     if search_phone:
          query += " AND base_user.contact LIKE %s"

     # Group by clause to ensure no duplicates and for aggregation (SUM)
     query += """
          GROUP BY appuser.roll_num, appuser.base_user_id, department.name, route.route_num, base_user.name, base_user.gender, base_user.contact, base_user.email, payment_status.status_name
     """

     # Parameters to safely insert the values into the query
     params = []
     if search_id:
          params.append(f"%{search_id}%")
     if search_name:
          params.append(f"%{search_name}%")
     if search_phone:
          params.append(f"%{search_phone}%")

     # Execute the raw query with parameters
     with connection.cursor() as cursor:
          cursor.execute(query, params)
          student_data = cursor.fetchall()

     # Convert query result into a list of dictionaries for easier use in the template
     students = []
     for row in student_data:
          student_info = {
     'student_name': row[0],   # Assuming 'row[0]' is student's name
     'gender': row[1],          # Assuming 'row[1]' is gender
     'roll_num': row[2],        # Assuming 'row[2]' is roll_num         # Assuming 'row[3]' is section
     'amount': row[3],          # Assuming 'row[4]' is amount
     'payment_status': row[4],  # Assuming 'row[5]' is payment status
     'phone': row[5],           # Assuming 'row[6]' is phone
     'email': row[6]            # Assuming 'row[7]' is email
     }

     return render(request, "transport/fee-collection.html", {"students": students, "search_id": search_id, "search_name": search_name, "search_phone": search_phone})


def add_route_view(request):
     return render(request, 'transport/add-route.html')



