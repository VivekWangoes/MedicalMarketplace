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
		(OTHER, 'Other')
	)

	doctor = models.OneToOneField(UserAccount, related_name='doctor_profile', on_delete=models.CASCADE)
	doctor_pic= models.ImageField(upload_to = 'images/', blank=True, null=True)
	gender = models.CharField(max_length=50, choices=GENDER_TYPE, blank=True, null=True)
	career_started = models.DateField(blank=True, null=True)
	specialty = models.CharField(max_length=50, blank=True, null=True)
	location_city = models.CharField(max_length=50, blank=True, null=True)
	clinic = models.CharField(max_length=100, blank=True, null=True)
	consultation_fees = models.IntegerField(blank=True, null=True)
	expertise_area = models.TextField(blank=True, null=True)
	verification = models.CharField(max_length=50, default=INCOMPLETED, blank=True, null=True)

	def __str__(self):
		return str(self.doctor)


class DoctorSlots(models.Model):
	slot_time = models.DateTimeField(blank=True, null=True)
	is_booked = models.BooleanField(default=False)

	def __str__(self):
		return str(self.slot_time)
		

class DoctorAvailability(models.Model):
	MORNING = 'MORNING'
	EVENING = 'EVENING'

	SLOT_TIME = (
			(MORNING, 'Morning'),
			(EVENING, 'EVENING')
	)

	doctor = models.ForeignKey(DoctorProfile, related_name='doctor_availabitily', on_delete=models.CASCADE)
	slot_date = models.DateField(blank=True, null=True)
	day = models.CharField(max_length=50, blank=True, null=True)
	slot = models.CharField(max_length=50, choices=SLOT_TIME, blank=True, null=True)
	time_slot = models.ManyToManyField(DoctorSlots)
	#daily = models.BooleanField(default=False)

	def __str__(self):
		return str(self.doctor)


class DoctorReviews(models.Model):
	doctor_data = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
	user_data = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
	review = models.TextField()
	prescription_rating = models.CharField(max_length=10, null=True, blank=True)
	explanation_rating = models.CharField(max_length=10, null=True, blank=True)
	friendliness_rating = models.CharField(max_length=10, null=True, blank=True)


class Appointments(models.Model):
	COMPLETED = "COMPLETED"
	UPCOMING = "UPCOMING"
	CANCLE = "CANCLE"

	STATUS_CHOICE = (
			(COMPLETED, 'Completed'),
			(UPCOMING, 'Upcoming'),
			(CANCLE, 'Cancle')
	)

	doctor = models.ForeignKey(DoctorProfile, related_name="doctor_appointment", on_delete=models.CASCADE)
	patient = models.ForeignKey(UserAccount, related_name="patient_appointment", on_delete=models.CASCADE)
	slot = models.OneToOneField(DoctorSlots, related_name='doctor_slot', on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICE, blank=True, null=True)

	def __str__(self):
		return "%s %s %s" % (self.doctor_id, self.patient_id, self.slot_id)