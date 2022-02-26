from django.contrib import admin
from .models import PatientProfile, Allergy, Medication, Disease, Injury, Surgery,\
	  PatientMedicalProfile, PatientLifeStyle
# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(Allergy)
admin.site.register(Medication)
admin.site.register(Disease)
admin.site.register(Injury)
admin.site.register(Surgery)
admin.site.register(PatientMedicalProfile)
admin.site.register(PatientLifeStyle)