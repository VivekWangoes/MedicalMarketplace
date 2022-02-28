""" patient/models.py """
from django.db import models
from accounts.models import UserAccount
from core.models import Base
from django.core.exceptions import ValidationError
from project.config.messages import Messages
from rest_framework import status

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
	is_prescription = models.BooleanField(default=False)

	def __str__(self):
		return str(self.name)


class LabTest(Base):
	name =  models.CharField(max_length=100)
	price = models.FloatField()

	def __str__(self):
		return str(self.name)


class MyCart(Base):
	patient_cart = models.ForeignKey(PatientProfile, related_name="patient_cart", on_delete=models.CASCADE)

	def __str__(self):
		return str(self.patient_cart)


class MyCartItem(Base):
	MEDICINE = "MEDICINE"
	LAB_TEST = "LAB_TEST"
	ITEM_CHOICE = (
		(MEDICINE, "Medicine"),
		(LAB_TEST, "Lab_Test")
	)

	mycart = models.ForeignKey(MyCart, related_name="mycart", on_delete=models.CASCADE)
	medicine = models.ForeignKey(Medicine, related_name="medicine_cart", on_delete=models.CASCADE, null=True, blank=True)
	lab_test = models.ForeignKey(LabTest, related_name="lab_test", on_delete=models.CASCADE, null=True, blank=True)
	quantity = models.IntegerField(null=True, blank=True)
	#total_price = models.FloatField(default=0, blank=True, null=True)
	address = models.ForeignKey(Address, related_name="address_cart", on_delete=models.CASCADE)
	prescription = models.FileField(upload_to = 'file/', blank=True, null=True)
	item_choice = models.CharField(max_length=50, choices=ITEM_CHOICE, null=True, blank=True)

	def __str__(self):
		return str(self.mycart)


	def save(self, *args, **kwargs):
		if self.medicine and self.lab_test:
			raise ValidationError(Messages.ONE_ITEM_ADD)
		if not self.medicine and not self.lab_test:
			raise ValidationError(Messages.NO_ITEM)
		else:
			super(MyCartItem, self).save(*args, **kwargs)




class OrderCart(Base):
	mycart_order = models.ForeignKey(MyCart, related_name='mycart_order', on_delete=models.CASCADE)

	def __str__(self):
		return str(self.order_cart)


class OrderItemConfirmed(Base):
	COMPLETED = "COMPLETED"
	YET_TO_BE_DELIVERED = "YET_TO_BE_DELIVERED"
	CANCLE = "CANCLE"
	STATUS_CHOICE = (
		(COMPLETED, "Completed"),
		(YET_TO_BE_DELIVERED, "Yet to be delivered"),
		(CANCLE, "Cancle")
	)
	order = models.ForeignKey(OrderCart, related_name='order_cart', on_delete=models.CASCADE)
	item = models.ForeignKey(MyCartItem, related_name='cart_item', on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICE, default=YET_TO_BE_DELIVERED)
	order_date = models.DateTimeField(auto_now=True, null=True, blank=True)
	delivery_date = models.DateTimeField(null=True, blank=True) 