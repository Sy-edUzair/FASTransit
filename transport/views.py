from django.shortcuts import render,redirect
from django.db import connection
from .models import *
from django.db.models import Sum
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render
from django.conf import settings
from .forms import *
from .models import *
from transport.models import *
from userauth.models import AppUser  
from noticeboard.models import *
from django.shortcuts import render
from django.db import connection
from .forms import RouteForm
from transport.models import TransportProvider

def dashboard(request):
    if request.user.is_transporter:
        total_vehicles = Vehicle.objects.count()
        total_routes = Route.objects.count()
        total_providers = TransportProvider.objects.count()
        recent_vehicles = Vehicle.objects.select_related('status', 'capacity_type', 'transport_provider')[:5]
        context = {
            'total_vehicles': total_vehicles,
            'total_routes': total_routes,
            'total_providers': total_providers,
            'recent_vehicles': recent_vehicles,
            'user': request.user
        }
        return render(request, 'transport/dashboard.html', context)
    else:
        return redirect(reverse('userauth:login'))


#@login_required(login_url=reverse_lazy("transport:transporter_login"))
def render_all_routes(request):
    if request.user.is_transporter:
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
    else:
       return redirect(reverse('userauth:login'))

@csrf_protect
def logout_view(request):
     logout(request)
     messages.success(request,"You logged out")
     return HttpResponseRedirect(reverse("userauth:login"))

def transport_driver_view(request):
    if request.user.is_transporter:
        raw_query = """SELECT 
        tp.id AS provider_id, 
        tp.name AS provider_name, 
        d.cnic AS driver_cnic, 
        d.name AS driver_name, 
        d.contact AS driver_contact, 
        d.license_number AS driver_license 
        FROM 
            transport_transportprovider tp
        LEFT JOIN 
            driver_driver d 
        ON 
            tp.id = d.appointed_provider_id
        WHERE 
            tp.id = %s; 
        """

        # Execute raw query to get providers with their drivers
        with connection.cursor() as cursor:
            appointed_provider =TransportProvider.objects.get(representative=request.user.providerrepresentative)
            cursor.execute(raw_query,[appointed_provider.id])
            results = cursor.fetchall()

        # If no results are returned, handle gracefully
        if not results:
            providers = []
        else:
            # Prepare data for rendering: group drivers by provider
            providers = {}
            for result in results:
                # Ensure there are enough elements in the result tuple
                if len(result) < 6:
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
    else:
        return redirect(reverse('userauth:login'))

def add_route_view(request):
    if request.user.is_transporter:
        if request.method == 'POST':
            form = RouteForm(request.POST)
            if form.is_valid():
                route_num = form.cleaned_data['route_num']
                start_stop = form.cleaned_data['start_stop']
                appointed_provider =TransportProvider.objects.get(representative=request.user.providerrepresentative)
                stops = form.cleaned_data['stops']
                stop_orders = form.cleaned_data.get('stop_orders', '').split(',')
                stop_orders = [order.strip() for order in stop_orders if order.strip()]

                try:
                    route = Route.objects.create(
                        route_num=route_num,
                        start_stop=start_stop,
                        appointed_provider=appointed_provider
                    )

                    for idx, stop in enumerate(stops):
                        # Get the corresponding stop order from the 'stop_orders' field
                        stop_order = stop_orders[idx] if idx < len(stop_orders) else idx + 1

                        RouteStop.objects.create(
                            route=route,
                            stop=stop,
                            stop_order=int(stop_order)
                        )               
                    route.stops.set(stops)
                    route.save()
                    # Display success message
                    messages.success(request, "Route added successfully!")
                    return redirect('transport:add-route')
                except Exception as e:
                    messages.error(request, f"Error occurred while adding route: {str(e)}")
        else:
            form = RouteForm()

        return render(request, 'transport/add-route.html', {'form': form})
    else:
        return redirect(reverse('userauth:login'))

def add_driver(request):
    if request.user.is_transporter:
        if request.method == "POST":
            form = DriverForm(request.POST)

            if form.is_valid():

                cnic = form.cleaned_data['cnic']
                name = form.cleaned_data['name']
                contact = form.cleaned_data['contact']
                license_number = form.cleaned_data['license_number']
                appointed_provider = TransportProvider.objects.get(representative=request.user.providerrepresentative)
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

                    messages.success(request, "Driver has been successfully added!")
                    return redirect('transport:add_driver')

                except Exception as e:
                    messages.error(request, f"Error occurred while adding driver: {str(e)}")
        else:
            form = DriverForm()

        return render(request, "transport/add_driver.html", {"form": form})
    else:
        return redirect(reverse('userauth:login'))

def view_routes(request):
    if request.user.is_transporter:
        raw_query = """SELECT 
        r.route_num, 
        r.start_stop_id, 
        s.name AS start_stop_name, 
        tp.name AS transport_provider_name
        FROM 
            transport_route r
        LEFT JOIN 
            transport_stop s 
        ON 
            r.start_stop_id = s.id
        JOIN 
            transport_transportprovider tp 
        ON 
            r.appointed_provider_id = tp.id
        WHERE 
            tp.id = %s;
        """

        try:
            appointed_provider = TransportProvider.objects.get(representative=request.user.providerrepresentative)
            with connection.cursor() as cursor:
                cursor.execute(raw_query,[appointed_provider.id])
                results = cursor.fetchall()
        except Exception as e:
            messages.error(request, f"Error occurred while fetching routes: {str(e)}")
            results = []

        routes = []
        for result in results:
            route_data = {
                "route_num": result[0],
                "start_stop_name": result[2],
                "transport_provider_name": result[3]
            }
            routes.append(route_data)

        return render(request, "transport/view_routes.html", {"routes": routes})
    else:
       return redirect(reverse('userauth:login'))

def add_vehicle(request):
    if request.user.is_transporter:
        if request.method == 'POST':
            form = VehicleForm(request.POST)
            if form.is_valid():
                license_plate = form.cleaned_data['license_plate']
                allotted_seats = form.cleaned_data['allotted_seats']
                tracking_id = form.cleaned_data['tracking_id']
                last_maintenance_date = form.cleaned_data['Last_maintenance_date']
                status = form.cleaned_data['status']
                capacity_type = form.cleaned_data['capacity_type']
                transport_provider = TransportProvider.objects.get(representative=request.user.providerrepresentative)
                route_no = form.cleaned_data['route_no']
                
             
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
                
       
                messages.success(request, 'Vehicle has been successfully added!')
                
                return redirect('transport:add_vehicle') 
            else:
                
                messages.error(request, 'Please fix the errors in the form.')
                return render(request, 'transport/add_vehicle.html', {'form': form})
        else:
            form = VehicleForm()
            return render(request, 'transport/add_vehicle.html', {'form': form})
    else:
        return redirect(reverse('userauth:login'))

def view_vehicles(request):
    if request.user.is_transporter:
        query = """
        SELECT
        vehicle.license_plate,
        vehicle.allotted_seats,
        vehicle.tracking_id,
        vehicle.Last_maintenance_date,
        vehicle.route_no_id  
        FROM
            transport_vehicle AS vehicle
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            vehicles = cursor.fetchall()
    
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

       
        if vehicle_list:
            messages.success(request, "Vehicles loaded successfully.")
        else:
            messages.warning(request, "No vehicles found.")

        return render(request, 'transport/view_vehicles.html', {'vehicles': vehicle_list})
    else:
        return redirect(reverse('userauth:login'))

def payment_status_view(request):
        users_paid = AppUser.objects.filter(payments__voucher__status__status_name="Succeeded").distinct()
        users_paid_with_amount = []
        for user in users_paid:
            total_paid = user.payments.aggregate(total=Sum('amount'))['total'] or 0
            users_paid_with_amount.append({
                'user': user,
                'total_paid': total_paid
            })

      
        users_not_paid = AppUser.objects.filter(vouchers__status__status_name="Pending").distinct()

        context = {
            'users_paid': users_paid_with_amount,
            'users_not_paid': users_not_paid,
        }
        return render(request, 'transport/view_fees_paid.html', context)
