""" patient/models.py """
from django.db import models
from accounts.models import UserAccount
from core.models import Base


class PatientProfile(Base, models.Model):
	patient = models.OneToOneField(UserAccount, related_name='patient_profile', on_delete=models.CASCADE)
	patient_pic= models.ImageField(upload_to = 'images/', blank=True, null=True)
	gender = models.CharField(max_length=20, null=True, blank=True)
	dob = models.DateTimeField(null=True, blank=True)
	emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
	emergency_contact_relation = models.CharField(max_length=255, null=True, blank=True)
	emergency_contact_phone = models.CharField(max_length=255, null=True, blank=True)
	location = models.CharField(null=True, blank=True, max_length=255)

	def __str__(self):
		return str(self.patient)


class Allergy(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return str(self.name)


class Medication(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return str(self.name)


class Disease(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	def __str__(self):
		return str(self.name)


class Injury(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	def __str__(self):
		return str(self.name)


class Surgery(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	def __str__(self):
		return str(self.name)


class PatientMedicalProfile(Base, models.Model):
	patient = models.OneToOneField(PatientProfile, related_name='patient_medical_profile', on_delete=models.CASCADE)
	height = models.CharField(max_length=20, null=True, blank=True)
	weight = models.CharField(max_length=50, null=True, blank=True)
	blood_group = models.CharField(max_length=50, null=True, blank=True)
	allergies = models.ManyToManyField(Allergy)
	medications = models.ManyToManyField(Medication, related_name='medication')
	past_medications = models.ManyToManyField(Medication, related_name='past_medication')
	cronic_dieseas = models.ManyToManyField(Disease)
	injuries = models.ManyToManyField(Injury)
	surgeries = models.ManyToManyField(Surgery)

	def __str__(self):
		return str(self.patient)


class PatientLifeStyle(Base, models.Model):
	patient = models.OneToOneField(PatientProfile, related_name='patient_life_style', on_delete=models.CASCADE)
	smoking_habits = models.TextField(null=True, blank=True)
	alchohol_consumption = models.TextField(null=True, blank=True)
	activity_level = models.TextField(null=True, blank=True)
	food_prefrence = models.TextField(null=True, blank=True)
	occupation = models.TextField(null=True, blank=True)

	def __str__(self):
		return str(self.patient)
