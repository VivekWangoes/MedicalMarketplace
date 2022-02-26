from django.db import models
from accounts.models import UserAccount
from core.models import Base

# Create your models here.
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

class Alergies(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return str(self.name)


class Medication(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)

	def __str__(self):
		return str(self.name)


class Dieseas(Base, models.Model):
	name = models.CharField(max_length=255, null=True, blank=True)
	def __str__(self):
		return str(self.name)


class Injuries(Base, models.Model):
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
	alergies = models.ManyToManyField(Alergies)
	medication = models.ManyToManyField(Medication, related_name='medication')
	past_medication = models.ManyToManyField(Medication, related_name='past_medication')
	cronic_dieseas = models.ManyToManyField(Dieseas)
	injuries = models.ManyToManyField(Injuries)
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


class Address(Base):
	HOME = "HOME"
	OFFICE = "OFFICE"
	OTHER = "OTHER"
	ADDRESS_CHOICES = (
		(HOME, "Home"),
		(OFFICE, "Office"),
		(OTHER, "Other")
	)
	patient = models.ForeignKey(PatientProfile, related_name="patient_address", on_delete=models.CASCADE)
	house_no_building_name = models.CharField(max_length=100)
	street_addr1 = models.CharField(max_length=100)
	street_addr2 = models.CharField(max_length=100)
	pincode = models.CharField(max_length=50)
	mobile_no = models.CharField(max_length=12)
	address_type = models.CharField(max_length=50, choices=ADDRESS_CHOICES)
	other = models.CharField(max_length=50, null=True, blank=True)
	name = models.CharField(max_length=50, null=True, blank=True)
	email = models.CharField(max_length=50, null=True, blank=True)

	def __str__(self):
		return str(self.patient)


class Medicine(Base):
	name =  models.CharField(max_length=100)
	solubility = models.CharField(max_length=50)
	company = models.CharField(max_length=100)
	price = models.FloatField()

	def __str__(self):
		return str(self.name)


class MyCart(Base):
	patient = models.ForeignKey(PatientProfile, related_name="patient_cart", on_delete=models.CASCADE)

	def __str__(self):
		return str(self.patient)


class MyCartItem(Base):
	mycart = models.ForeignKey(MyCart, related_name="mycart", on_delete=models.CASCADE)
	medicine = models.ForeignKey(Medicine, related_name="medicine_cart", on_delete=models.CASCADE)
	quantity = models.IntegerField()
	address = models.ForeignKey(Address, related_name="address_cart", on_delete=models.CASCADE)
	prescription = models.FileField(upload_to = 'file/', blank=True, null=True)

	def __str__(self):
		return str(self.mycart_item)