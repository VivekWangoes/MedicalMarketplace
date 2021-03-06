from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.models import Base


class UserAccountManager(BaseUserManager):
    def create_user(self, email, name='', password=None, mobile_no=None, offer=False, role=None, term_condition=False):
        if not email:
            raise ValueError('user must have an email')

        email = self.normalize_email(email.lower())
        user = self.model(email=email, name=name, mobile_no=mobile_no, role=role,
                          offer=offer, term_condition=term_condition)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password, mobile_no=None, offer=False, role=0, term_condition=True):
        user = self.create_user(email, name, password, mobile_no, offer, role, term_condition)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.set_password(password)
        user.save()
        return user


class UserAccount(Base, AbstractBaseUser, PermissionsMixin):
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
        (PATIENT, 'PATIENT')
    )

    role = models.IntegerField(choices=ROLE_TYPES, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    email_otp = models.CharField(max_length=5,null=True, blank=True)
    email_otp_created = models.DateTimeField(null=True, blank=True)
    login_otp = models.CharField(max_length=5,null=True, blank=True)
    login_otp_created = models.DateTimeField(null=True, blank=True)
    mobile_no = models.CharField(max_length=12, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True, default="")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=USER_STATUSES, default=ACTIVE)
    offer = models.BooleanField(default=False)
    term_condition = models.BooleanField(default=False)
    
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BlackListedToken(Base):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(UserAccount, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class ContactSupport(Base):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

