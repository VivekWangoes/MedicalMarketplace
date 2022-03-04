from django.db import models
from accounts.models import UserAccount
from core.models import Base
from patient.models import PatientProfile
# Create your models here.


class DoctorProfile(Base):
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
	rating = models.IntegerField(default=0)
	booking_fees = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return str(self.doctor)

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class DoctorSlot(Base):
	slot_time = models.DateTimeField(blank=True, null=True)
	is_booked = models.BooleanField(default=False)

	def __str__(self):
		return str(self.slot_time)
		

class DoctorAvailability(Base):
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
	time_slot = models.ManyToManyField(DoctorSlot)

	def __str__(self):
		return str(self.doctor)

	def save(self, *args, **kwargs):
		self.full_clean()
		super().save(*args, **kwargs)


class DoctorReview(Base):
	doctor = models.ForeignKey(DoctorProfile, related_name='doctor_profile', on_delete=models.CASCADE, null=True, blank=True)
	patient = models.ForeignKey(PatientProfile, related_name='patient_profile',on_delete=models.CASCADE, null=True, blank=True)
	review = models.TextField()
	prescription_rating = models.CharField(max_length=10, null=True, blank=True)
	explanation_rating = models.CharField(max_length=10, null=True, blank=True)
	friendliness_rating = models.CharField(max_length=10, null=True, blank=True)


class Appointment(Base):
	COMPLETED = "COMPLETED"
	UPCOMING = "UPCOMING"
	CANCLE = "CANCLE"
	STATUS_CHOICE = (
		(COMPLETED, 'Completed'),
		(UPCOMING, 'Upcoming'),
		(CANCLE, 'Cancle')
	)
	doctor = models.ForeignKey(DoctorProfile, related_name="doctor_appointments", on_delete=models.CASCADE)
	patient = models.ForeignKey(PatientProfile, related_name="patient_appointments", on_delete=models.CASCADE, blank=True, null=True)
	slot = models.OneToOneField(DoctorSlot, related_name='doctor_slot', on_delete=models.CASCADE)
	status = models.CharField(max_length=50, choices=STATUS_CHOICE, blank=True, null=True)
	#term_condition = models.BooleanField(default=False, null=True, blank=True)
	def __str__(self):
		return "%s %s %s" % (self.doctor, self.patient, self.slot)


class ConsultationDetail(Base):
	appointment = models.OneToOneField(Appointment, related_name="consultation", on_delete=models.CASCADE)
	notes = models.TextField()
	medication = models.CharField(max_length=50, null=True, blank=True)
	lab_test = models.CharField(max_length=50, null=True, blank=True)
	next_appointment = models.ForeignKey(Appointment, related_name='next_appointment', on_delete=models.CASCADE, null=True, blank=True)
	health_status = models.CharField(max_length=50, blank=True, null=True)