""" doctor/tests/test_models.py """
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from PIL import Image
from io import StringIO, BytesIO
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile
from doctor.models import (
	DoctorProfile,
	DoctorSlot,
	DoctorAvailability,
	DoctorReview,
	Appointment
)

from accounts.models import UserAccount

from datetime import datetime
import pytest
import uuid


class BaseTestCase(TestCase):

	def create_image(self, storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
		"""
		Generate a test image, returning the filename that it was saved as.

		If ``storage`` is ``None``, the BytesIO containing the image data
		will be passed instead.
		"""
		import pdb; pdb.set_trace()
		# by_str = bytes('Hello', 'utf-8')
		# data = BytesIO(by_str)
		# Image.new(image_mode, size).save(data, image_format)
		source_image = Image.new(mode="RGB", size=(200, 200))
		byte_data = BytesIO()
		source_image.save(byte_data, format='JPEG') # Save resize image to bytes
		media_content = ContentFile(image)

		if not storage:
		   return media_content
		image_file = ContentFile(data.read())
		return storage.save(filename, image_file)

	@pytest.mark.django_db
	def create_user(self, **kwargs):
		return UserAccount.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_doctor_profile(self, **kwargs):
		return DoctorProfile.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_doctor_slots(self, **kwargs):
		return DoctorSlot.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_doctor_availability(self, **kwargs):
		availability = DoctorAvailability(**kwargs)
		availability.save()
		availability.time_slot.add(self.doctor_slot)
		return availability

	@pytest.mark.django_db
	def create_doctor_reviews(self, **kwargs):
		review = DoctorReview(**kwargs)
		review.save()
		return review

	@pytest.mark.django_db
	def create_appointment(self, **kwargs):
		appointment = Appointment(**kwargs)
		appointment.save()
		return appointment

	def setUp(self):
		self.email = 'johndoe@gmail.com'
		self.user_data = {
			'role': UserAccount.DOCTOR,
			'email': self.email,
			'name': 'John',
			'otp': '12345',
			'mobile_no': '9977665544',
			'last_name': 'Doe',
			'is_staff': False,
			'is_superuser': False,
			'is_active': True,
			'is_email_verified': False,
			'device_id': '1',
			'password': 'testing321'
		}
		self.user = self.create_user(**self.user_data)

		self.specialty = 'Pathologist'
		self.career_started = datetime.today().date()
		self.location_city = 'Indore'
		self.clinic = 'Hansraj Clinic'
		self.fees = 500
		self.expertise_area = 'Expert in Diagnosing Disease of particular patient'

		self.doctor_profile_data = {
			'doctor': self.user,
			'gender': DoctorProfile.MALE,
			'career_started': self.career_started,
			'specialty' : self.specialty,
			'location_city': self.location_city,
			'clinic': self.clinic,
			'consultation_fees': self.fees,
			'expertise_area': self.expertise_area,
			'verification': DoctorProfile.INCOMPLETED
		}
		self.doctor_profile = self.create_doctor_profile(**self.doctor_profile_data)

		self.slot_time = datetime.today()
		self.doctor_slot_data = {
			'slot_time' : self.slot_time,
			'is_booked' : True
		}
		self.doctor_slot = self.create_doctor_slots(**self.doctor_slot_data)

		self.slot_date = datetime.today().date()
		self.day = 'Sunday'
		self.doctor_availability_data = {
			'doctor' : self.doctor_profile,
			'slot_date' : self.slot_date,
			'day' : self.day,
			'slot' : DoctorAvailability.MORNING,
		}
		self.doctor_availability = self.create_doctor_availability(**self.doctor_availability_data)

		self.review = "Doctor's treatment is very good"
		self.prescription_rating = '4'
		self.explanation_rating = "Four"
		self.friendliness_rating = '9'

		self.doctor_review_data = {
			'doctor_data' : self.doctor_profile,
			'user_data' : self.user,
			'review' : self.review,
			'prescription_rating' : self.prescription_rating,
			'explanation_rating' : self.explanation_rating,
			'friendliness_rating': self.friendliness_rating
		}
		self.doctor_review = self.create_doctor_reviews(**self.doctor_review_data)

		self.appointment_data = {
			'doctor' : self.doctor_profile,
			'patient' : self.user,
			'slot' : self.doctor_slot,
			'status' : Appointment.COMPLETED
		}
		self.appointment = self.create_appointment(**self.appointment_data)


class DoctorProfileTestCase(BaseTestCase):
	"""
	DoctorProfile Test Case
	"""

	def test_object_created(self):
		"""
		test object created
		"""
		doctor_profiles = DoctorProfile.objects.all()
		self.assertEqual(doctor_profiles.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.doctor_profile, DoctorProfile)

	def test_doctor_field_value_type(self):
		self.assertIsInstance(self.doctor_profile.doctor, UserAccount)

	def test_doctor_field_value(self):
		self.assertEqual(self.doctor_profile.doctor, self.user)

	def test_doctor_related_name_value(self):
		self.assertEqual(self.user.doctor_profile, self.doctor_profile)

	# def test_if_doctor_pic_uploaded_successfully(self):
	# 	avatar = self.create_image(None, 'avatar.png')
	# 	avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
	# 	print(avatar_file)

	# def test_doctor_pic_upload_with_non_image_file(self):
	# 	pass

	def test_gender_field_default_choice(self):
		self.assertEqual(self.doctor_profile.gender, DoctorProfile.MALE)

	def test_gender_field_with_updated_value(self):
		self.doctor_profile.gender = DoctorProfile.FEMALE
		self.doctor_profile.save()
		self.assertEqual(self.doctor_profile.gender, DoctorProfile.FEMALE)

	def test_gender_field_with_wrong_choice(self):
		self.assertNotEqual(self.doctor_profile.gender, DoctorProfile.FEMALE)

	def test_career_started_field_value(self):
		self.assertEqual(self.doctor_profile.career_started, self.career_started)

	def test_speciality_field_value(self):
		self.assertEqual(self.doctor_profile.specialty, self.specialty)

	def test_location_city_field_value(self):
		self.assertEqual(self.doctor_profile.location_city, self.location_city)

	def test_clinic_field_value(self):
		self.assertEqual(self.doctor_profile.clinic, self.clinic)

	def test_consultation_fee_field_value(self):
		self.assertEqual(self.doctor_profile.consultation_fees, self.fees)

	def test_consultation_fee_field_updation_with_char_value(self):
		self.doctor_profile.consultation_fees = '600'
		self.doctor_profile.save()
		self.assertEqual(self.doctor_profile.consultation_fees, 600)

	def test_expertise_area_field_value(self):
		self.assertEqual(self.doctor_profile.expertise_area, self.expertise_area)

	def test_verification_field_default_value(self):
		self.assertEqual(self.doctor_profile.verification, DoctorProfile.INCOMPLETED)

	def test_verification_field_with_updated_value(self):
		self.doctor_profile.verification = 'COMPLETED'
		self.doctor_profile.save()
		self.assertEqual(self.doctor_profile.verification, 'COMPLETED')

	def test_verification_field_with_wrong_value(self):
		self.assertNotEqual(self.doctor_profile.verification, 'COMPLETED')

	def test_str_method(self):
		self.assertEqual(self.doctor_profile.__str__(), self.email)


class DoctorSlotTestCase(BaseTestCase):
	"""
	Doctor Slot Test Case
	"""

	def test_object_created(self):
		doctor_slots = DoctorSlot.objects.all()
		self.assertEqual(doctor_slots.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.doctor_slot, DoctorSlot)

	def test_slot_time_value(self):
		self.assertEqual(self.doctor_slot.slot_time, self.slot_time)

	def test_is_booked_value(self):
		self.assertEqual(self.doctor_slot.is_booked, True)

	def test_str_method(self):
		self.assertEqual(self.doctor_slot.__str__(), str(self.slot_time))

	def test_str_method_if_slot_time_is_null(self):
		self.doctor_slot_data1 = {
			'is_booked' : True
		}
		self.doctor_slot1 = self.create_doctor_slots(**self.doctor_slot_data1)
		self.assertEqual(self.doctor_slot1.__str__(), 'None')


class DoctorAvailabilityTestCase(BaseTestCase):

	def test_object_created(self):
		doctor_availabilities = DoctorAvailability.objects.all()
		self.assertEqual(doctor_availabilities.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.doctor_availability, DoctorAvailability)

	def test_doctor_field_value_type(self):
		self.assertIsInstance(self.doctor_availability.doctor, DoctorProfile)

	def test_doctor_field_value(self):
		self.assertEqual(self.doctor_availability.doctor, self.doctor_profile)

	def test_doctor_related_name_value(self):
		self.assertEqual(self.doctor_availability.doctor, self.doctor_profile)

	def test_slot_date_field_value(self):
		self.assertEqual(self.doctor_availability.slot_date, self.slot_date)

	def test_day_field_value(self):
		self.assertEqual(self.doctor_availability.day, self.day)

	def test_slot_field_default_value(self):
		self.assertEqual(self.doctor_availability.slot, DoctorAvailability.MORNING)

	def test_slot_field_updated_value(self):
		self.doctor_availability.slot = DoctorAvailability.EVENING
		self.doctor_availability.save()
		self.assertEqual(self.doctor_availability.slot, DoctorAvailability.EVENING)

	def test_slot_field_wrong_value(self):
		self.assertNotEqual(self.doctor_availability.slot, DoctorAvailability.EVENING)

	def test_time_slot_field_default_value(self):
		self.assertEqual(self.doctor_availability.time_slot.all().first(), self.doctor_slot)

	def test_time_slot_field_add_time_slot_check_count(self):
		self.slot_time1 = datetime.today()
		self.doctor_slot_data1 = {
			'slot_time' : self.slot_time1,
			'is_booked' : True
		}
		self.doctor_slot1 = self.create_doctor_slots(**self.doctor_slot_data1)
		self.doctor_availability.time_slot.add(self.doctor_slot1)
		self.assertEqual(self.doctor_availability.time_slot.all().count(), 2)

	def test_str_method(self):
		self.assertEqual(self.doctor_availability.__str__(), str(self.doctor_profile))


class DoctorReviewTestCase(BaseTestCase):

	def test_object_created(self):
		doctor_reviews = DoctorReview.objects.all() 
		self.assertEqual(doctor_reviews.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.doctor_review, DoctorReview)

	def test_doctor_data_field_type(self):
		self.assertIsInstance(self.doctor_review.doctor_data, DoctorProfile)

	def test_doctor_data_field_value(self):
		self.assertEqual(self.doctor_review.doctor_data, self.doctor_profile)

	def test_user_data_field_type(self):
		self.assertIsInstance(self.doctor_review.user_data, UserAccount)

	def test_user_data_field_value(self):
		self.assertEqual(self.doctor_review.user_data, self.user)

	def test_review_field_value(self):
		self.assertEqual(self.doctor_review.review, self.review)

	def test_prescription_rating_field_value(self):
		self.assertEqual(self.doctor_review.prescription_rating, self.prescription_rating)

	def test_explanation_rating_field_value(self):
		self.assertEqual(self.doctor_review.explanation_rating, self.explanation_rating)

	def test_friendliness_rating_field_value(self):
		self.assertEqual(self.doctor_review.friendliness_rating, self.friendliness_rating)


class AppointmentTestCase(BaseTestCase):

	def test_object_created(self):
		appointments = Appointment.objects.all()
		self.assertEqual(appointments.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.appointment, Appointment)

	def test_doctor_field_type(self):
		self.assertIsInstance(self.appointment.doctor, DoctorProfile)

	def test_doctor_field_value(self):
		self.assertEqual(self.appointment.doctor, self.doctor_profile)

	def test_doctor_field_related_name(self):
		self.assertEqual(self.doctor_profile.doctor_appointments.all()[0], self.appointment)

	def test_patient_field_type(self):
		self.assertIsInstance(self.appointment.patient, UserAccount)

	def test_patient_field_value(self):
		self.assertEqual(self.appointment.patient, self.user)

	def test_patient_field_related_name(self):
		self.assertEqual(self.user.patient_appointments.all()[0], self.appointment)

	def test_slot_field_type(self):
		self.assertIsInstance(self.appointment.slot, DoctorSlot)

	def test_slot_field_value(self):
		self.assertEqual(self.appointment.slot, self.doctor_slot)

	def test_slot_field_related_name(self):
		self.assertEqual(self.doctor_slot, self.doctor_slot)

	def test_status_field_value(self):
		self.assertEqual(self.appointment.status, Appointment.COMPLETED)

	def test_str_method(self):
		string_data = f'{self.doctor_profile.id} {self.user.id} {self.doctor_slot.id}'
		self.assertEqual(self.appointment.__str__(), string_data)

	