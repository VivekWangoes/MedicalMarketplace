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
	gender = models.CharField(max_length=50, choices=GENDER_TYPE, blank=True, null=True)
	experience = models.CharField(max_length=50, blank=True, null=True)
	specialty = models.CharField(max_length=50, blank=True, null=True)
	location_city = models.CharField(max_length=50, blank=True, null=True)
	verification = models.CharField(max_length=50,default=INCOMPLETED, blank=True, null=True)


	def __str__(self):
		return str(self.doctor)


class DoctorInfo(models.Model):
	doctor = models.OneToOneField(UserAccount, related_name='doctor_info', on_delete=models.CASCADE)
	clinic = models.CharField(max_length=100, blank=True, null=True)
	consultation_fees = models.IntegerField(blank=True, null=True)
	experties_area = models.TextField(blank=True, null=True)

	def __str__(self):
		return str(self.doctor)


class DoctorAvailability(models.Model):
	doctor = models.ForeignKey(DoctorProfile, related_name='doctor_availabitily', on_delete=models.CASCADE)
	year = models.IntegerField()
	month = models.CharField(max_length=50)
	date = models.IntegerField(null=True,blank=True)
	day = models.CharField(max_length=50,null=True,blank=True)
	from_available = models.CharField(max_length=50)
	to_available = models.CharField(max_length=50)
	daily = models.BooleanField(default=False)

	def __str__(self):
		return str(self.doctor)