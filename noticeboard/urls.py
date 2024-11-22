from django.urls import path
from . import views  

app_name = 'noticeboard'

urlpatterns = [
    path('noticeboard/', views.notice_board, name='noticeboard'),
]
