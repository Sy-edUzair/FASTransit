from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns=[
    path("",views.dashboard,name="dashboard"),
    path("signup/",views.signup_view,name="signup"),    
    path("login/",views.login_view,name="login"),  
    path("logout",views.logout_view,name="logout"),  
    path("point-card",views.point_card_view,name='point-card'),
]