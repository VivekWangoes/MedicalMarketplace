from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from project.settings.dev import EMAIL_HOST_USER
from datetime import datetime


class UserAccountManager(BaseUserManager):
    def create_user(self,  email, name, mobile_no, password, role):
        if not email:
            raise ValueError('user must have an email')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, mobile_no=mobile_no, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, mobile_no, password, role):
        print("super user")
        user = self.create_user(email, name, mobile_no, password,role)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        # user.role = UserAccount.SUPER_ADMIN
        user.set_password(password)
        user.save()
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    SUPER_ADMIN = 0
    DOCTOR = 1
    PATIENT = 2

    INACTIVE = 'INACTIVE'
    ACTIVE = 'ACTIVE'
    DELETED = 'DELETED'
    PENDING = 'PENDING'
    PROFILE_INCOMPLETE = 'PROFILE_INCOMPLETE'
    UNQUALIFIED = 'UNQUALIFIED'
    APPROVED = 'APPROVED'
    ATTENTION = 'ATTENTION'

    USER_STATUSES = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
        # applicable for clinic only
        (PENDING, 'Pending Approval'),
        (PROFILE_INCOMPLETE, 'Profile Incomplete'),
    )

    ROLE_TYPES = (
        (SUPER_ADMIN, 'SUPER_ADMIN'),
        (DOCTOR, 'DOCTOR'),
        (PATIENT, 'PATIENT'),
        
    )

    role = models.IntegerField(choices=ROLE_TYPES)
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=150)
    otp = models.CharField(max_length=5,null=True, blank=True)
    otp_created = models.DateTimeField(default=datetime.now(),blank=True,null=True)
    mobile_no = models.CharField(max_length=12)
    last_name = models.CharField(max_length=150, null=True, blank=True, default="")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=USER_STATUSES, default=ACTIVE)
    

    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','mobile_no','role']

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(UserAccount, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class ContactSupport(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)




# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

#     email_plaintext_message = "{}{}?token={}".format('http://127.0.0.1:8000/',reverse('password_reset:reset-password-request'), reset_password_token.key)

#     send_mail(
#         # title:
#         "Password Reset for {title}".format(title="Your Account"),
#         # message:
#         email_plaintext_message,
#         # from:
#         EMAIL_HOST_USER,
#         # to:
#         [reset_password_token.user.email]
#     )






