from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability, DoctorSlot, Appointment, DoctorReview
# Register your models here.
admin.site.register(DoctorProfile)
admin.site.register(DoctorSlot)
admin.site.register(DoctorAvailability)
admin.site.register(Appointment)
admin.site.register(DoctorReview)