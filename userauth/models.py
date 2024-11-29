from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.core.validators import RegexValidator
from transport.models import Route
from django.contrib.auth.hashers import make_password

Gender=(
    ("Male","Male"),
    ("Female","Female"),
    ("Other","N/S"),
)

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

#Custom User Model Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
# Custom User Model
class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=11)
    gender = models.CharField(choices=Gender,max_length=10,default="male")
    profile_image = models.ImageField(upload_to="profiles",null=True, blank=True)
    is_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_transporter = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = CustomUserManager()

    USERNAME_FIELD = "email" 
    REQUIRED_FIELDS = ['name'] #fields needed when creating superuser
    
class AppUser(models.Model):
    roll_num_validator = RegexValidator(
        regex=r'^\d{2}[A-Z]-\d{4}$', 
        message='Roll number must be in the format XXK-XXXX, e.g., 22K-4586.'
    )
    roll_num = models.CharField(
        max_length = 9,
        primary_key = True,
        validators = [roll_num_validator]
    )
    Address=models.CharField(max_length=200)
    cnic=models.CharField(max_length=13,unique=True)
    emergency_contact=models.CharField(max_length=11)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,null=True,blank=True)
    assigned_route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    base_user= models.OneToOneField(CustomUser, on_delete=models.CASCADE)


    def __str__(self):
        return self.roll_num
    @property
    def imageURL(self):
        try:
            URL = self.base_user.profile_image.url
        except:
            URL= ' '
        return URL
    
class ProviderRepresentative(models.Model):
    cnic_validator = RegexValidator(
        regex=r'^\d{5}-\d{7}-\d{1}$', 
        message='CNIC must be in the format XXXX-XXXXXXXX-X'
    )
    representative_cnic = models.CharField(
        max_length=15,
        primary_key=True,
        validators = [cnic_validator]
        )
    base_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.base_user.name
    
    @property
    def imageURL(self):
        try:
            URL = self.base_user.profile_image.url
        except:
            URL= ' '
        return URL