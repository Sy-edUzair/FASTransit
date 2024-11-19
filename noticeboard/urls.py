from django.urls import path
from . import views  

urlpatterns = [
    
    path('notice-board/', views.notice_board, name='noticeboard'),
]
