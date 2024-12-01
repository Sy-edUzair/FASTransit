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

    context = {
        'total_vehicles': total_vehicles,
        'total_routes': total_routes,
        'total_providers': total_providers,
        'recent_vehicles': recent_vehicles
    }
    return render(request, 'transport/dashboard.html', context)

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