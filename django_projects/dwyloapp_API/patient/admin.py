from django.contrib import admin
from .models import PatientProfile, Alergies, Medication, Dieseas, Injuries, Surgery,\
	  PatientMedicalProfile, PatientLifeStyle
# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(Alergies)
admin.site.register(Medication)
admin.site.register(Dieseas)
admin.site.register(Injuries)
admin.site.register(Surgery)
admin.site.register(PatientMedicalProfile)
admin.site.register(PatientLifeStyle)