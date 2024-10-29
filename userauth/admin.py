from django.contrib import admin
from userauth.models import User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=['name','roll_num','email']

admin.site.register(User,UserAdmin)