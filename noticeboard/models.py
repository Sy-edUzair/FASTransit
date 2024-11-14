from django.db import models
from userauth.models import User
# Create your models here.
class ComplaintStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='feedbacks')
    comments = models.TextField()
    rating = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    complaint_status = models.ForeignKey(ComplaintStatus, on_delete=models.SET_NULL, null=True)

    
class Notice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name ='notices')
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)



