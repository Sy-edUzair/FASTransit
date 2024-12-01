from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns=[
    path("",views.dashboard,name="dashboard"),
    path("signup/",views.signup_view,name="signup"),    
    path("login/",views.login_view,name="login"),  
    path("logout/",views.logout_view,name="logout"),  
    path("point-card/",views.point_card_view,name='point-card'),
    path("user-profile/",views.user_profile_view,name='user-profile'),
    path("landing-page/",views.landing_page_view,name='landing-page'),
    path("landing-page2/",views.landing_page2_view,name='landing-page2'),
    path("provider-details/",views.provider_detail_view,name='provider-details'),
    path("feedback/",views.feedback_view,name='feedback'),
    path("tracking/",views.tracking_view,name="tracking"),
]