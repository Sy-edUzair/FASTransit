from django.db import models
from userauth.models import User
from django.db import connection
from django.core.mail import send_mail
from django.utils.timezone import now

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

class Notification(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save the notification

        if is_new:
            self.send_email_notification()

    def send_email_notification(self):
        # Raw SQL query 
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM userauth_user WHERE email IS NOT NULL")
            recipient_emails = [row[0] for row in cursor.fetchall()] 

        send_mail(
            subject=self.title,  
            message=self.message,  
            from_email="tahatahir09@gmail.com", 
            recipient_list=recipient_emails,  
        )

    def __str__(self):
        return self.title

class Notice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name ='notices')
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)




