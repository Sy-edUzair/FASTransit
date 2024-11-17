from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import *
from .models import User
import os

# Create your views here.
def dashboard(request):
     return render(request,'index.html')

def login_view(request):
     if request.method=="POST":
          username=request.POST.get('email')
          password=request.POST.get('password')
          
          if not User.objects.filter(username=username).exists():
               messages.error(request,'Invalid Username')
               return redirect('/login')

          user=authenticate(username=username,password=password)
          if user is None:
               messages.error(request,'Invalid Password')
               return HttpResponseRedirect(reverse('userauth:login'))
          # Redirect to dashboard
          # return redirect()
     return render(request,'userauth/login.html')

@csrf_protect
def signup_view(request):
     if request.method == "POST":
          form = UserForm(request.POST)
          if form.is_valid():
               roll_num = form.cleaned_data.get('roll_num')
               name = form.cleaned_data.get('name')
               email = request.POST.get('email')
               address = form.cleaned_data.get('Address')
               cnic = form.cleaned_data.get('cnic')
               contact = form.cleaned_data.get('contact')
               emergency_contact = form.cleaned_data.get('emergency_contact')
               gender = form.cleaned_data.get('gender')
               department = form.cleaned_data.get('department')  
               profile_image = request.FILES.get('profile_image')  
               password = form.cleaned_data.get('password')
               confirm_password = form.cleaned_data.get('password2')

               if password != confirm_password:
                    messages.error(request, 'Passwords do not match.')
                    return HttpResponseRedirect(reverse('userauth:signup'))
               
               print(profile_image)
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
                    print(f"Uploaded file name: {profile_image_path}")


               with connection.cursor() as cursor:
                    cursor.execute(
                         """SELECT COUNT(*) FROM userauth_user WHERE roll_num = %s""", [roll_num])
                    if cursor.fetchone()[0] > 0:
                         messages.error(request, 'Roll number already exists.')
                         return HttpResponseRedirect(reverse('userauth:signup'))
               
                    cursor.execute(
                         """SELECT COUNT(*) FROM userauth_user WHERE email = %s """,[email]
                    )
                    if cursor.fetchone()[0] > 0:
                         messages.error(request,'Email Already exists.')
                         return HttpResponseRedirect(reverse('userauth:signup'))
                    try:
                         cursor.execute("BEGIN")
                         cursor.execute("""
                              INSERT INTO userauth_user(password,roll_num,email,name,address,cnic,contact,emergency_contact,gender,profile_image,is_staff,is_superuser) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,FALSE,FALSE) RETURNING roll_num
                         """,[make_password(password),roll_num,email,name, address, cnic, contact,emergency_contact, gender, profile_image_path]
                         )

                         user_roll_num = cursor.fetchone()[0]

                         # Update department if provided
                         if department:
                              cursor.execute("""SELECT id FROM userauth_department WHERE name = %s""",[department])
                              dept_id = cursor.fetchone()[0]
                              cursor.execute("""UPDATE userauth_user SET department_id = %s WHERE roll_num = %s""", [dept_id, user_roll_num])

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
          form=UserForm()

     return render(request, 'userauth/signup.html',{'form':form})

