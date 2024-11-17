from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns=[
    path("",views.dashboard,name="dashboard"),
    path("signup/",views.signup_view,name="signup"),    
    path("login/",views.login_view,name="login"),  
    # path("userauth/logout",views.logout_view,name="logout"),  
]