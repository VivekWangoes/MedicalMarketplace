from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability, DoctorSlots, Appointments
# Register your models here.
admin.site.register(DoctorProfile)
admin.site.register(DoctorSlots)
admin.site.register(DoctorAvailability)
admin.site.register(Appointments)