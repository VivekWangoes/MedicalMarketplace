from django.contrib import admin
from .models import DoctorProfile, DoctorInfo, DoctorAvailability
# #Register your models here.
admin.site.register(DoctorProfile)
admin.site.register(DoctorInfo)
admin.site.register(DoctorAvailability)
