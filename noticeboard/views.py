from django.shortcuts import render
from django.db import connection
from .models import Notification

def notice_board(request):
    raw_query = """
        SELECT id, title, message, created_at, is_active 
        FROM noticeboard_notification 
        WHERE is_active = TRUE 
        ORDER BY created_at DESC
    """
    notifications = Notification.objects.raw(raw_query)
    return render(request, "noticeboard/notice_board.html", {"notifications": notifications})
