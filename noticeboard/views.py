from django.shortcuts import render
from django.db import connection
from django.conf import settings
from .models import *
from django.contrib.auth.decorators import login_required

@login_required(login_url=settings.LOGIN_URL)
def notice_board(request):
    raw_query = """
        SELECT *
        FROM noticeboard_notice
        WHERE is_active = TRUE 
        ORDER BY date_posted DESC
    """
    notices = Notice.objects.raw(raw_query)
    return render(request, "noticeboard/notice_board.html", {"notices": notices})
