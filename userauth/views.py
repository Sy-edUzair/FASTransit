from django.views.decorators.csrf import csrf_protect
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .models import User
# Create your views here.
def dashboard(request):
     return render(request,'index.html')

def login_view(request):
     if request.method=="POST":
          username=request.POST.get('username')
          password=request.POST.get('password')
          
     if not User.objects.filter(username=username).exists():
          messages.error(request,'Invalid Username')
          return redirect('/login')

     user=authenticate(username=username,password=password)
     if user is None:
          messages.error(request,'Invalid Password')
          return redirect('/login')
     else:
          login_view(request,user)
          # Redirect to dashboard
          # return redirect()
     return render(request,'index.html')

@csrf_protect
def signup_view(request):
     if request.method == "POST":
          roll_num = request.POST.get('roll_num')
          name = request.POST.get('name')
          email = request.POST.get('email')
          Address = request.POST.get('Address')
          cnic = request.POST.get('cnic')
          contact = request.POST.get('contact')
          emergency_contact = request.POST.get('emergency_contact')
          gender = request.POST.get('gender')
          department_id = request.POST.get('department')  
          assigned_route_id = request.POST.get('assigned_route') 
          profile_image = request.FILES.get('profile_image')  
          password = request.POST.get('password')
          confirm_password = request.POST.get('confirm_password')

          if User.objects.filter(email=email).exists():
               messages.error(request, 'Email already exists.')
               return redirect('/signup/')
          if User.objects.filter(roll_num=roll_num).exists():
               messages.error(request, 'Roll number already exists.')
               return redirect('/signup/')
          if password != confirm_password:
               messages.error(request, 'Passwords do not match.')
               return redirect('/signup/')

          user = User.objects.create(
          roll_num=roll_num,
          name=name,
          email=email,
          Address=Address,
          cnic=cnic,
          contact=contact,
          emergency_contact=emergency_contact,
          gender=gender,
          profile_image=profile_image,
     )


     if department_id:
          from .models import Department
          department = Department.objects.filter(id=department_id).first()
          if department:
               user.department = department

          if assigned_route_id:
               from .models import Route
               route = Route.objects.filter(id=assigned_route_id).first()
               if route:
                    user.assigned_route = route

          user.set_password(password)
          user.save()

          messages.success(request, 'User created successfully.')
          return redirect('/login/')

     return render(request, 'userauth/login.html')

