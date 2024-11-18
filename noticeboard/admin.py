from django.contrib import admin
from .models import *


class ComplaintStatusAdmin(admin.ModelAdmin):
    list_display = ['status_id', 'status_name']
    search_fields = ['status_name', ] 

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'rating', 'submitted_at', 'responded_at', 'complaint_status']
    search_fields = ['user__username', 'comments']  
    list_filter = ['rating', 'complaint_status'] 

class NoticeAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'date_posted']
    search_fields = ['user__username', 'title', 'message']  
    list_filter = ['date_posted',] 


admin.site.register(ComplaintStatus,ComplaintStatusAdmin)
admin.site.register(Feedback,FeedbackAdmin)
admin.site.register(Notice,NoticeAdmin)