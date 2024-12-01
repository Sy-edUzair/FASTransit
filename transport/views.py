from django.shortcuts import render,redirect
from django.db import connection
from .models import *
from django.db.models import Sum
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
from userauth.models import ProviderRepresentative
from transport.models import TransportProvider

def dashboard(request):
    total_vehicles = Vehicle.objects.count()
    total_routes = Route.objects.count()
    total_providers = TransportProvider.objects.count()
    recent_vehicles = Vehicle.objects.select_related('status', 'capacity_type', 'transport_provider')[:5]

<<<<<<< HEAD
    context = {
        'total_vehicles': total_vehicles,
        'total_routes': total_routes,
        'total_providers': total_providers,
        'recent_vehicles': recent_vehicles
    }
    return render(request, 'transport/dashboard.html', context)
=======
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
>>>>>>> e66ffd644dec956633fdad37f56160100b840fd5

@csrf_protect
def logout_view(request):
     logout(request)
     messages.success(request,"You logged out")
     return HttpResponseRedirect(reverse("transport:transporter_login"))

def transport_driver_view(request):
    # Query to get all transport providers and their drivers
    raw_query = """
        SELECT tp.id AS provider_id, tp.name AS provider_name, 
           d.cnic AS driver_cnic, d.name AS driver_name, 
           d.contact AS driver_contact, d.license_number AS driver_license 
    FROM transport_transportprovider tp
    LEFT JOIN driver_driver d ON tp.id = d.appointed_provider_id
    """

    # Execute raw query to get providers with their drivers
    with connection.cursor() as cursor:
        cursor.execute(raw_query)
        results = cursor.fetchall()
        
        # Debugging: Print results to check the structure
        print("Query Results:", results)

    # If no results are returned, handle gracefully
    if not results:
        print("No data returned by query!")
        providers = []
    else:
        # Prepare data for rendering: group drivers by provider
        providers = {}
        for result in results:
            # Ensure there are enough elements in the result tuple
            if len(result) < 6:
                print("Skipping incomplete result:", result)
                continue  # Skip if the result doesn't have the expected number of columns

            provider_id = result[0]
            provider_name = result[1]
            driver_cnic = result[2]
            driver_name = result[3]
            driver_contact = result[4]
            driver_license = result[5]

            # Add driver under the correct provider
            if provider_id not in providers:
                providers[provider_id] = {
                    "provider_name": provider_name,
                    "drivers": []
                }

            providers[provider_id]["drivers"].append({
                "driver_cnic": driver_cnic,
                "driver_name": driver_name,
                "driver_contact": driver_contact,
                "driver_license": driver_license,
            })
        
        # Convert dictionary to a list for rendering
        providers_list = [{"provider_name": provider["provider_name"], "drivers": provider["drivers"]} for provider in providers.values()]

    # Render the template with the grouped providers and drivers
    return render(request, "transport/driver-detail.html", {"providers": providers_list})

def add_route_view(request):
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            # Save the route to the database
            route_num = form.cleaned_data['route_num']
            start_stop = form.cleaned_data['start_stop']
            appointed_provider = form.cleaned_data['appointed_provider']
            stops = form.cleaned_data['stops']

            try:
                # Create the Route instance
                route = Route.objects.create(
                    route_num=route_num,
                    start_stop=start_stop,
                    appointed_provider=appointed_provider
                )

<<<<<<< HEAD
                # Add stops to the route through the many-to-many relationship
                route.stops.set(stops)
                route.save()

                # Display success message
                messages.success(request, "Route added successfully!")
                return redirect('transport:add-route')  # Redirect to the same page after adding
            except Exception as e:
                messages.error(request, f"Error occurred while adding route: {str(e)}")
    else:
        form = RouteForm()

    return render(request, 'transport/add-route.html', {'form': form})

def add_driver(request):
    if request.method == "POST":
        form = DriverForm(request.POST)

        if form.is_valid():
            # Debugging: Print cleaned data
            print("Form cleaned data:", form.cleaned_data)

            cnic = form.cleaned_data['cnic']
            name = form.cleaned_data['name']
            contact = form.cleaned_data['contact']
            license_number = form.cleaned_data['license_number']
            appointed_provider = form.cleaned_data['appointed_provider']
            appointed_vehicle = form.cleaned_data['appointed_vehicle']

            try:
                # Manually create the driver
                driver = Driver(
                    cnic=cnic,
                    name=name,
                    contact=contact,
                    license_number=license_number,
                    appointed_provider=appointed_provider,
                    appointed_vehicle=appointed_vehicle
                )
                driver.save()  # Save the driver instance to the database

                # Check if the data is actually inserted
                print("Driver data inserted:", driver)

                messages.success(request, "Driver has been successfully added!")
                return redirect('transport:add_driver')

            except Exception as e:
                print(f"Error occurred while adding driver: {str(e)}")
                messages.error(request, f"Error occurred while adding driver: {str(e)}")

    
    else:
        form = DriverForm()

    return render(request, "transport/add_driver.html", {"form": form})

def view_routes(request):
    # Adjust query based on actual database schema
    raw_query = """
        SELECT r.route_num, r.start_stop_id, r.appointed_provider_id, 
               s.name AS start_stop_name, tp.name AS transport_provider_name
        FROM transport_route r
        LEFT JOIN transport_stop s ON r.start_stop_id = s.id
        LEFT JOIN transport_transportprovider tp ON r.appointed_provider_id = tp.id
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            results = cursor.fetchall()
            print("Query Results:", results)  # For debugging purposes

    except Exception as e:
        messages.error(request, f"Error occurred while fetching routes: {str(e)}")
        results = []

    # Preparing routes data for rendering
    routes = []
    for result in results:
        route_data = {
            "route_num": result[0],
            "start_stop_name": result[3],
            "transport_provider_name": result[4]
        }
        routes.append(route_data)

    return render(request, "transport/view_routes.html", {"routes": routes})

def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():  # Validate the form before accessing cleaned_data
            # Now you can safely access cleaned_data
            license_plate = form.cleaned_data['license_plate']
            allotted_seats = form.cleaned_data['allotted_seats']
            tracking_id = form.cleaned_data['tracking_id']
            last_maintenance_date = form.cleaned_data['Last_maintenance_date']
            status = form.cleaned_data['status']
            capacity_type = form.cleaned_data['capacity_type']
            transport_provider = form.cleaned_data['transport_provider']
            route_no = form.cleaned_data['route_no']
            
            # Now save the data to the database or perform other actions
            new_vehicle = Vehicle(
                license_plate=license_plate,
                allotted_seats=allotted_seats,
                tracking_id=tracking_id,
                Last_maintenance_date=last_maintenance_date,
                status=status,
                capacity_type=capacity_type,
                transport_provider=transport_provider,
                route_no=route_no
            )
            new_vehicle.save()
            
            # Success message
            messages.success(request, 'Vehicle has been successfully added!')
            
            return redirect('transport:add_vehicle')  # Redirect to the same page or a success page
        else:
            # If the form is not valid, render the form again with errors
            messages.error(request, 'Please fix the errors in the form.')
            return render(request, 'transport/add_vehicle.html', {'form': form})
    else:
        form = VehicleForm()  # Create an empty form for GET requests
        return render(request, 'transport/add_vehicle.html', {'form': form})

def view_vehicles(request):
    # Raw MySQL query to fetch all vehicles
    query = """
    SELECT
    vehicle.license_plate,
    vehicle.allotted_seats,
    vehicle.tracking_id,
    vehicle.Last_maintenance_date,
    vehicle.route_no_id  -- Assuming `route_no` is a foreign key
FROM
    transport_vehicle AS vehicle
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        vehicles = cursor.fetchall()

    # Process the result into a more readable format
    vehicle_list = []
    for vehicle in vehicles:
        vehicle_data = {
            'license_plate': vehicle[0],
            'allotted_seats': vehicle[1],
            'tracking_id': vehicle[2],
            'Last_maintenance_date': vehicle[3],
            'route_no': vehicle[4]
        }
        vehicle_list.append(vehicle_data)

    # Example of adding messages for success or warning
    if vehicle_list:
        messages.success(request, "Vehicles loaded successfully.")
    else:
        messages.warning(request, "No vehicles found.")

    return render(request, 'transport/view_vehicles.html', {'vehicles': vehicle_list})

def payment_status_view(request):
    users_paid = AppUser.objects.filter(payments__status__status_name="Paid").distinct()
    users_paid_with_amount = []
    for user in users_paid:
        total_paid = user.payments.aggregate(total=Sum('amount'))['total'] or 0
        users_paid_with_amount.append({
            'user': user,
            'total_paid': total_paid
        })

    # Query users who haven't paid
    users_not_paid = AppUser.objects.filter(payments__status__status_name="Unpaid").distinct()

    # Pass to context
    context = {
        'users_paid': users_paid_with_amount,
        'users_not_paid': users_not_paid,
    }
    return render(request, 'transport/view_fees_paid.html', context)
=======

>>>>>>> e66ffd644dec956633fdad37f56160100b840fd5
