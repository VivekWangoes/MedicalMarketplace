from django.db import models
from accounts.models import UserAccount

# Create your models here.

class DoctorProfile(models.Model):
	MALE = 'MALE'
	FEMALE = 'FEMALE'
	OTHER = 'OTHER'

	INCOMPLETED = 'Incompleted'

	GENDER_TYPE = (
		(MALE, 'Male'),
		(FEMALE, 'Female'),
		(OTHER, 'Other'))

	doctor = models.OneToOneField(UserAccount, related_name='doctor_profile', on_delete=models.CASCADE)
	gender = models.CharField(max_length=50, choices=GENDER_TYPE)
	experience = models.CharField(max_length=50)
	specialty = models.CharField(max_length=50)
	location_city = models.CharField(max_length=50)
	verification = models.CharField(max_length=50,default=INCOMPLETED)


	def __str__(self):
		return str(self.doctor)


class DoctorInfo(models.Model):
	doctor = models.OneToOneField(UserAccount, related_name='doctor_info', on_delete=models.CASCADE)
	clinic = models.CharField(max_length=100)
	consultation_fees = models.IntegerField()
	experties_area = models.TextField()

	def __str__(self):
		return str(self.doctor)


class DoctorAvailability(models.Model):
	doctor = models.ForeignKey(UserAccount, related_name='doctor_availabitily', on_delete=models.CASCADE)
	year = models.IntegerField()
	month = models.CharField(max_length=50)
	date = models.IntegerField()
	day = models.CharField(max_length=50)
	from_available = models.CharField(max_length=50)
	to_available = models.CharField(max_length=50)
	daily = models.BooleanField(default=False)

	def __str__(self):
		return str(self.doctor)