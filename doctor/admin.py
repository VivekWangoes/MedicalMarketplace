from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(DoctorProfile)

admin.site.register(DoctorSlot)

admin.site.register(DoctorAvailability)

admin.site.register(Appointment)

admin.site.register(DoctorReview)

admin.site.register(ConsultationDetail)

admin.site.register(DoctorSetTime)