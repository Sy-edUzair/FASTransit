from django.urls import path
from . import views  

urlpatterns = [
    path('noticeboard/', views.notice_board, name='noticeboard'),
]
