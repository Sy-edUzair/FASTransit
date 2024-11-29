from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import *

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'name', 'is_staff', 'is_superuser', 'is_user', 'is_transporter')
    list_filter = ('is_staff', 'is_superuser', 'is_user', 'is_transporter', 'gender')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('name', 'contact', 'gender', 'profile_image')}),
        (('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_user', 'is_transporter', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_user', 'is_transporter')}
        ),
    )
    search_fields = ('email', 'name')
    ordering = ('email',)


class AppUserAdmin(admin.ModelAdmin):
    list_display = ['roll_num', 'base_user_email', 'base_user_name']
    search_fields = ['roll_num', 'cnic']
    
    def base_user_name(self, obj):
        return obj.base_user.name
    base_user_name.short_description = 'Name'

    def base_user_email(self, obj):
        return obj.base_user.email
    base_user_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):
        # Use the custom save method from the form to handle base_user creation
        form.save(commit=True)

# Register your models here
class ProviderRepAdmin(admin.ModelAdmin):
    list_display = ['base_user_name', 'base_user_email', 'base_user_contact']

    def base_user_name(self, obj):
        return obj.base_user.name
    base_user_name.short_description = 'Name'

    def base_user_email(self, obj):
        return obj.base_user.email
    base_user_email.short_description = 'Email'

    def base_user_contact(self, obj):
        return obj.base_user.contact
    base_user_contact.short_description = 'Contact'
    list_per_page = 20

class DepartmentAdmin(admin.ModelAdmin):
    list_display=['name']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AppUser,AppUserAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(ProviderRepresentative,ProviderRepAdmin)