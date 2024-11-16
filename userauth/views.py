from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .forms import *

# Create your views here.
def dashboard(request):
     return render(request,'index.html')

def login_view(request):
     return render(request,'userauth/login.html')

@csrf_protect
def signup_view(request):
     return render(request,'userauth/signup.html',{'form':UserForm})
