from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.conf import settings
from .forms import *
from .models import *
from transport.models import *
from noticeboard.models import *
import os

# Create your views here.

@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
     raw_query = """
          SELECT * 
          FROM noticeboard_notice
          WHERE is_active = TRUE
          ORDER BY date_posted DESC
          """
     Notices = Notice.objects.raw(raw_query)
     raw_query_2= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query_2)
     return render(request,'index3.html',{'user':request.user,'notices':Notices,'providers':providers})      

@csrf_protect
def login_view(request):
     if request.method=="POST":
          form = LoginForm(request.POST)
          if form.is_valid():
               email = form.cleaned_data['email']
               password = form.cleaned_data['password']
               try:
                    user = CustomUser.objects.get(email__iexact=email)# using email since it is a unique field
                    auth_user = authenticate(request,username=email,password=password)
                    print(auth_user)
                    if auth_user is not None:
                         if user.is_user:
                              try:
                                   appuser_instance = user.appuser
                                   login(request,auth_user)
                                   messages.success(request,"You are logged in")
                                   return HttpResponseRedirect(reverse('userauth:dashboard'))
                              except:
                                   messages.warning(request,f"User with {email} does not exist")
                         elif user.is_transporter:
                              try:
                                   rep_instance = user.providerrepresentative
                                   login(request,auth_user)
                                   messages.success(request,"You are logged in")
                                   return HttpResponseRedirect(reverse('transport:transport-dashboard'))
                              except:
                                   messages.warning(request,f"Provider Rep with {email} does not exist")
                    else:
                         messages.warning(request,"Incorrect Credentials, Please Try Again!")
               except:
                    messages.warning(request,f"User with {email} does not exist")
     else:
          form = LoginForm()
     context={
          'form':form
     }
     return render(request,"userauth/login.html",context)

@csrf_protect
def logout_view(request):
    logout(request)
    messages.success(request,"You logged out")
    return HttpResponseRedirect(reverse("userauth:login"))

@csrf_protect
def signup_view(request):
     if request.method == "POST":
          user_form = CustomUserForm(request.POST, request.FILES)
          app_user_form = AppUserForm(request.POST)
          if user_form.is_valid() and app_user_form.is_valid():
               email = user_form.cleaned_data.get('email')
               name = user_form.cleaned_data.get('name')
               contact = user_form.cleaned_data.get('contact')
               gender = user_form.cleaned_data.get('gender')
               profile_image = user_form.cleaned_data.get('profile_image')
               password = user_form.cleaned_data.get('password')
               confirm_password = user_form.cleaned_data.get('password2')

               if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return HttpResponseRedirect(reverse('userauth:signup'))
               
               profile_image_path = None
               if profile_image:
               # Save file and get path
                    file_name = profile_image.name
                    upload_path = os.path.join(settings.MEDIA_ROOT, 'profiles', file_name)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    with open(upload_path, 'wb+') as destination:
                         for chunk in profile_image.chunks():
                              destination.write(chunk)
                    profile_image_path = f'profiles/{file_name}'
                   
               with connection.cursor() as cursor:
                    cursor.execute(
                         """SELECT COUNT(*) FROM userauth_customuser WHERE email = %s""",[email]
                    )
                    if cursor.fetchone()[0] > 0:
                         messages.error(request,'Email Already exists.')
                         return HttpResponseRedirect(reverse('userauth:signup'))
                    
                    cursor.execute("""INSERT INTO userauth_customuser (email, name, contact, gender, profile_image, password, is_user) VALUES (%s, %s, %s, %s, %s, %s, %s)""", [email, name, contact, gender, profile_image_path, make_password(password), True])
                     
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    user_id = cursor.fetchone()[0]
           
                    roll_num = app_user_form.cleaned_data.get('roll_num')
                    address = app_user_form.cleaned_data.get('Address')
                    cnic = app_user_form.cleaned_data.get('cnic')
                    emergency_contact = app_user_form.cleaned_data.get('emergency_contact')
                    department = app_user_form.cleaned_data.get('department')  

                    cursor.execute(
                         """SELECT COUNT(*) FROM userauth_appuser WHERE roll_num = %s""", [roll_num])
                    if cursor.fetchone()[0] > 0:
                         messages.error(request, 'Roll number already exists.')
                         return HttpResponseRedirect(reverse('userauth:signup'))
                    
                    try:
                         cursor.execute("BEGIN")
                         cursor.execute("""INSERT INTO userauth_appuser (roll_num, Address, cnic, emergency_contact,base_user_id)VALUES (%s, %s, %s, %s, %s) RETURNING roll_num""", [roll_num, address, cnic, emergency_contact,user_id])

                         user_roll_num = cursor.fetchone()[0]
                         print(user_roll_num)

                         # Update department if provided
                         if department:
                              cursor.execute("""SELECT id FROM userauth_department WHERE name = %s""",[department])
                              dept_id = cursor.fetchone()[0]
                              cursor.execute("""UPDATE userauth_appuser SET department_id = %s WHERE roll_num = %s""", [dept_id, user_roll_num])

                              # Commit transaction
                         cursor.execute("COMMIT")
                         
                         messages.success(request, 'User created successfully.')
                         return HttpResponseRedirect(reverse('userauth:login'))
                    except Exception as e:
                         # Rollback in case of error
                         cursor.execute("ROLLBACK")
                         messages.error(request, f'Error creating user: {str(e)}')
                         return HttpResponseRedirect(reverse('userauth:signup'))
     else:
          user_form = CustomUserForm()
          app_user_form = AppUserForm()
     return render(request, 'userauth/signup.html',{'user_form': user_form,'app_user_form': app_user_form})

def point_card_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "userauth/point_card.html",{"providers":providers,'user':request.user,})

def user_profile_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "userauth/user-profile.html",{"providers":providers,'user':request.user,})
def landing_page_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "userauth/landing-page.html",{"providers":providers,'user':request.user,})
def landing_page2_view(request):
     raw_query= """
          SELECT * 
          FROM transport_transportprovider
          """
     providers = TransportProvider.objects.raw(raw_query)
     return render(request, "userauth/landing-page2.html",{"providers":providers,'user':request.user,})