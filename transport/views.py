from django.shortcuts import render
from django.db import connection
from .models import *
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.conf import settings
from .forms import *
from .models import *
from transport.models import *
from noticeboard.models import *


def render_route_page(request):
    # raw_query = """
    #     SELECT *
    #     FROM noticeboard_notice
    #     WHERE is_active = TRUE 
    #     ORDER BY date_posted DESC
    # """
    # notices = Notice.objects.raw(raw_query)
    return render(request, "transport/routes.html")

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
          
               try:
                    provider_rep = ProviderRepresentative.objects.get(email__iexact=email)# using email since it is a unique field
                    auth_user = authenticate(request,username=email,password=password)
          
                    if auth_user is not None:
                         login(request,auth_user)
                         messages.success(request,"You are logged in")
                         return HttpResponseRedirect(reverse('userauth:dashboard'))
                    else:
                         messages.warning(request,"Incorrect Password, Please Try Again!")
                         print("Incorrect Password, Please Try Again!")
               except:
                    messages.warning(request,f"User with {email} does not exist")
                    print(f"User with {email} does not exist")
     else:
          form = transportLoginForm()
     context={
          'form':form
     }
     return render(request, "transport/transporter-login.html", context)

def transporter_dashboard(request):
    # raw_query = """
    #     SELECT *
    #     FROM noticeboard_notice
    #     WHERE is_active = TRUE 
    #     ORDER BY date_posted DESC
    # """
    # notices = Notice.objects.raw(raw_query)
    return render(request, "transport/transport-dashboard.html", {})