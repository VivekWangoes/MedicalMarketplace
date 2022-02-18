from django.db import models
from accounts.models import UserAccount


# Create your models here.
class PatientProfile(models.Model):
	patient = models.OneToOneField(UserAccount, related_name='patient_profile', on_delete=models.CASCADE)
	gender = models.CharField(max_length=20, null=True, blank=True)
	dob = models.DateTimeField(null=True, blank=True)
	emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
	emergency_contact_relation = models.CharField(max_length=255, null=True, blank=True)
	emergency_contact_phone = models.CharField(max_length=255, null=True, blank=True)
	location = models.CharField(null=True, blank=True, max_length=255)

class Alergies(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

class Medication(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

class Dieseas(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

class Injuries(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

class Surgery(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

class PatientMedicalProfile(models.Model):
	patient = models.OneToOneField(PatientProfile, related_name='patient_medical_profile', on_delete=models.CASCADE)
	height = models.CharField(max_length=20, null=True, blank=True)
	weight = models.CharField(max_length=50, null=True, blank=True)
	blood_group = models.CharField(max_length=50, null=True, blank=True)
	alergies = models.ManyToManyField(Alergies)
	medication = models.ManyToManyField(Medication, related_name='medication')
	past_medication = models.ManyToManyField(Medication, related_name='past_medication')
	cronic_dieseas = models.ManyToManyField(Dieseas)
	injuries = models.ManyToManyField(Injuries)
	surgeries = models.ManyToManyField(Surgery)

class PatientLifeStyle(models.Model):
	patient = models.OneToOneField(PatientProfile, related_name='patient_life_style', on_delete=models.CASCADE)
	smoking_habits = models.TextField(null=True, blank=True)
	alchohol_consumption = models.TextField(null=True, blank=True)
	activity_level = models.TextField(null=True, blank=True)
	food_prefrence = models.TextField(null=True, blank=True)
	occupation = models.TextField(null=True, blank=True)