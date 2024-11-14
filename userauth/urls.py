from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns=[
    path("userauth/sign-up/",views.register_view,name="sign-up"),    
    # path("userauth/login/",views.login_view,name="login"),  
    # path("userauth/logout",views.logout_view,name="logout"),  
]