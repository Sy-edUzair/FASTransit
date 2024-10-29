from django.db import models
from userauth.models import User
# Create your models here.

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.TextField()
    rating = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    complaint_status = models.ForeignKey('ComplaintStatus', on_delete=models.SET_NULL, null=True)

class ComplaintStatus(models.Model):
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name


class NoticeBoard(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    notice_board = models.ForeignKey(NoticeBoard, on_delete=models.SET_NULL, null=True)



