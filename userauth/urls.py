from django.urls import path
from userauth import views

app_name = "userauth"

urlpatterns=[
    path("",views.login_view,name="login"),  
    path("user-dashboard/",views.dashboard,name="dashboard"),
    path("signup/",views.signup_view,name="signup"),    
    path("logout/",views.logout_view,name="logout"),  
    path("point-card/",views.point_card_view,name='point-card'),
    path("download-point-card/",views.generate_card_pdf,name="card-pdf"),
    path("user-profile/",views.user_profile_view,name='user-profile'),
    path("provider-details/",views.provider_detail_view,name='provider-details'),
    path("feedback/",views.feedback_view,name='feedback'),
    path("tracking/",views.tracking_view,name="tracking"),
    path("render-routes/",views.render_route_page,name="render-routes"),
    path("select-stop/",views.select_stop,name="select-stop")
]