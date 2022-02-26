from django.contrib import admin
# Dieseas,Injuries, allergies
from .models import PatientProfile, Allergy, Medication, Disease,\
	 Injury, Surgery, PatientMedicalProfile, PatientLifeStyle, Address,\
 	 Medicine, MyCart, MyCartItem
# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(Allergy)
admin.site.register(Medication)
admin.site.register(Disease)
admin.site.register(Injury)
admin.site.register(Surgery)
admin.site.register(PatientMedicalProfile)
admin.site.register(PatientLifeStyle)
admin.site.register(Address)
admin.site.register(Medicine)
admin.site.register(MyCart)
admin.site.register(MyCartItem)