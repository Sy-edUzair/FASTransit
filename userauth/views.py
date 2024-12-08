from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
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
from transport.forms import *
from .models import *
from transport.models import *
from noticeboard.models import *
from noticeboard.forms import *
from payment.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from transport.forms import SelectRouteForm
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import os
import qrcode

@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
     if request.user.is_user:
          raw_query = """
               SELECT * 
               FROM noticeboard_notice
               WHERE is_active = TRUE
               ORDER BY date_posted DESC
               """
          Notices = Notice.objects.raw(raw_query)
          
          return render(request,'index3.html',{'user':request.user,'notices':Notices}) 
     else:
          return redirect(reverse('userauth:login'))
        

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

                    cursor.execute("""SELECT COUNT(*) FROM userauth_appuser WHERE roll_num = %s""", [roll_num])
                    if cursor.fetchone()[0] > 0:
                         messages.error(request, 'Roll number already exists.')
                         return HttpResponseRedirect(reverse('userauth:signup'))
                    
                    try:
                         cursor.execute("BEGIN")
                         cursor.execute("""INSERT INTO userauth_appuser (roll_num, Address, cnic, emergency_contact,base_user_id)VALUES (%s, %s, %s, %s, %s) RETURNING roll_num""", [roll_num, address, cnic, emergency_contact,user_id])

                         user_roll_num = cursor.fetchone()[0]
                         
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

@login_required(login_url=settings.LOGIN_URL)
def point_card_view(request):
     if request.user.is_user:
          voucher = Voucher.objects.filter(user=request.user.appuser,due_date__gt=now(),status__status_name='Pending').last()
          return render(request, "userauth/point_card.html",{'user':request.user,'voucher':voucher})
     else:
          return redirect(reverse('userauth:login'))

@login_required(login_url=settings.LOGIN_URL)
def user_profile_view(request):
     if request.user.is_user:
          return render(request, "userauth/user-profile.html",{'user':request.user,})
     else:
          return redirect(reverse('userauth:login'))
     

@login_required(login_url=settings.LOGIN_URL)
def feedback_view(request):
     if request.user.is_user:
          raw_query2="""SELECT * FROM noticeboard_feedback"""
          feedbacks = Feedback.objects.raw(raw_query2)
          if request.method == "POST":
               form = FeedbackForm(request.POST)
               if form.is_valid():
                         comments = form.cleaned_data['comments']
                         user_id = request.user.appuser.roll_num
                         with connection.cursor() as cursor:
                              cursor.execute("SELECT status_id FROM noticeboard_complaintstatus WHERE status_name = %s LIMIT 1", ["Pending"])
                              complaint_status_id = cursor.fetchone() 
                              query = """
                              INSERT INTO noticeboard_feedback (user_id, comments,submitted_at,responded_at, complaint_status_id)
                              VALUES (%s, %s, NOW(),NULL,%s)
                              """
                              with connection.cursor() as cursor:
                                   cursor.execute(query, [user_id, comments, complaint_status_id[0]])
                         messages.success(request,"Feedback Submitted!")
          else:
               form = FeedbackForm()
          return render(request, "userauth/feedback.html",{'feedbacks':feedbacks,'user':request.user,"form":form})
     else:
          return redirect(reverse('userauth:login'))


@login_required(login_url=settings.LOGIN_URL)
def tracking_view(request):
     if request.user.is_user:
          # playstore_url = "https://play.google.com/store/search?q=cyber%20track&c=apps&hl=es_419"
          # qr = qrcode.QRCode(
          #      version=1,
          #      error_correction=qrcode.constants.ERROR_CORRECT_L,
          #      box_size=10,  
          #      border=4, 
          # )
          # qr.add_data(playstore_url)
          # qr.make(fit=True)

          # # Create an image from the QR code
          # img = qr.make_image(fill="black", back_color="white")

          # # Save the image or display it
          # img.save("static/img/cybertrack_qr_code.png")
          # img.show() 

          return render(request,"transport/tracking.html")
     else:
          return redirect(reverse('userauth:login'))

@login_required(login_url=settings.LOGIN_URL)
def provider_detail_view(request):
     if request.user.is_user:
          assigned_provider=request.user.appuser.assigned_route.appointed_provider
          assigned_rep = assigned_provider.representative
          return render(request, "provider-details.html",{'user':request.user,'assigned_provider':assigned_provider,'assigned_rep':assigned_rep})
     else:
          return redirect(reverse('userauth:login'))
     
def render_route_page(request):
     if request.user.is_user:
          raw_query_2= """
          SELECT r.route_num AS route_num, s.id AS stop_id, s.name AS stop_name FROM transport_route AS r JOIN transport_routestop AS rs ON r.route_num = rs.route_id JOIN transport_stop AS s ON rs.stop_id = s.id ORDER BY r.route_num, rs.stop_order;
          """
          with connection.cursor() as cursor:
            cursor.execute(raw_query_2)
            results = cursor.fetchall()

          #Organize results into a structure suitable for the template
          routes = {}
          for route_num, stop_id, stop_name in results:
               if route_num not in routes:
                    idx=0
                    routes[route_num] = {"stops": []}
               if stop_id:
                    idx+=1
                    routes[route_num]["stops"].append({"idx":idx,"id": stop_id, "name": stop_name})

          if request.method == 'POST':
               form = SelectRouteForm(request.POST)
               if form.is_valid():
                    if not request.user.appuser.assigned_route:
                         user = AppUser.objects.get(roll_num=request.user.appuser.roll_num)
                         status = PaymentStatus.objects.get(status_name='Pending')
                         current_date = datetime.now()
                         due_date = current_date + relativedelta(months=+2)
                         Voucher.objects.create(user=user,semester='Fall 2025',status=status,amount=39000,due_date=due_date)
                    route_number = form.cleaned_data['route_number']
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT route_num FROM transport_route WHERE route_num = %s", [route_number])
                        route = cursor.fetchone()
                        if route:
                            route_id = route[0]
                            cursor.execute(
                                "UPDATE userauth_appuser SET assigned_route_id = %s WHERE roll_num = %s",
                                [route_id, request.user.appuser.roll_num]
                                )
                            messages.success(request,f"Route {route_number} assigned to user {request.user.appuser.roll_num}.")
                            #Notify admin and provider about route change
                            return redirect(reverse('userauth:select-stop'))
                        else:
                            messages.error(request,f"Route {route_number} not found.")
          else:
               form = SelectRouteForm()
          return render(request, "transport/routes.html",{"routes": routes,"form":form})
     else:
          return redirect(reverse('userauth:login'))

def select_stop(request):
     if request.user.is_user:
          raw_query_2= """
          SELECT r.route_num AS route_num, s.id AS stop_id, s.name AS stop_name FROM transport_route AS r JOIN transport_routestop AS rs ON r.route_num = rs.route_id JOIN transport_stop AS s ON rs.stop_id = s.id ORDER BY r.route_num, rs.stop_order;
          """
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
               stops_form = SelectStopForm(request.POST,selected_route=request.user.appuser.assigned_route.route_num)

               if stops_form.is_valid():
                    selected_stop = stops_form.cleaned_data['start_stop']
                    with connection.cursor() as cursor:
                         cursor.execute(
                         "UPDATE userauth_appuser SET stop_id = %s WHERE roll_num = %s",
                         [selected_stop.id, request.user.appuser.roll_num]
                         )
                    request.user.appuser.refresh_from_db()
                    messages.success(request,f"Stop {selected_stop.name} assigned to user {request.user.appuser.roll_num}.")
                    #Notify provider and admin about stop change
          else:
               stops_form = SelectStopForm(selected_route=request.user.appuser.assigned_route.route_num)
          return render(request, "transport/select_stop.html", {
            "form": stops_form,
            "routes": routes
          })
     else:
          return redirect(reverse('userauth:login'))
     
def generate_card_pdf(request):
     if request.user.is_user:
          image_path = os.path.join(settings.MEDIA_ROOT, request.user.profile_image.name)
          
          context={"user":request.user,'image_path': image_path}
          html_string = render_to_string('userauth/download-point-template.html', context)

          response = HttpResponse(content_type='application/pdf')
          response['Content-Disposition'] = f'attachment; filename="{request.user.appuser.roll_num}pointcard.pdf"'
          
     
          pisa_status = pisa.CreatePDF(html_string, dest=response)
          if pisa_status.err:
               return HttpResponse('Error generating PDF', status=500)
          return response
     else:
          return redirect(reverse('userauth:login'))