from django.contrib import admin
from .models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=['name','roll_num','email']

class DepartmentAdmin(admin.ModelAdmin):
    list_display=['name']

admin.site.register(User,UserAdmin)
admin.site.register(Department,DepartmentAdmin)