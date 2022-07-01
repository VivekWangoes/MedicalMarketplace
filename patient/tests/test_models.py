""" patient/tests/test_models.py """
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from patient.models import (
	PatientProfile, Allergy, Medication, Disease, Injury,
	Surgery, PatientMedicalProfile, PatientLifeStyle
)
from accounts.models import UserAccount

import pytest
import io


class BaseTestCase(TestCase):

	@pytest.mark.django_db
	def create_user(self, **kwargs):
		return UserAccount.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_patient_profile(self, **kwargs):
		patient_pic = kwargs.pop('patient_pic')
		profile = PatientProfile(**kwargs)
		profile.patient_pic = patient_pic
		profile.save()
		return profile

	@pytest.mark.django_db
	def create_allergy(self, **kwargs):
		return Allergy.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_medication(self, **kwargs):
		return Medication.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_disease(self, **kwargs):
		return Disease.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_injury(self, **kwargs):
		return Injury.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_surgery(self, **kwargs):
		return Surgery.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_patient_medical_profile(self, **kwargs):
		allergies = []
		if kwargs.get('allergies'):
			allergies = kwargs.pop('allergies')

		medications = []
		if kwargs.get('medications'):
			medications = kwargs.pop('medications')

		past_medications = []
		if kwargs.get('past_medications'):
			past_medications = kwargs.pop('past_medications')

		cronic_dieseas = []
		if kwargs.get('cronic_dieseas'):
			cronic_dieseas = kwargs.pop('cronic_dieseas')

		injuries = []
		if kwargs.get('injuries'):
			injuries = kwargs.pop('injuries')

		surgeries = []
		if kwargs.get('surgeries'):
			surgeries = kwargs.pop('surgeries')

		medical_profile = PatientMedicalProfile(**kwargs)
		medical_profile.save()

		medical_profile.allergies.set(allergies)
		medical_profile.medications.set(medications)
		medical_profile.past_medications.set(past_medications)
		medical_profile.cronic_dieseas.set(cronic_dieseas)
		medical_profile.injuries.set(injuries)
		medical_profile.surgeries.set(surgeries)

		return medical_profile

	@pytest.mark.django_db
	def create_patient_lifestyle(self, **kwargs):
		profile = kwargs.pop('patient')
		patient_lifestyle = PatientLifeStyle(**kwargs)
		patient_lifestyle.profile = profile
		patient_lifestyle.save()
		return patient_lifestyle

	def create_dummy_pic(self, **kwargs):
		# import pdb; pdb.set_trace()
		image_path = '/home/wangoesgeet/Projects/dwyloapp/django_projects/dwyloapp_API/patient/tests/test_data/dummy_pic.jpeg'
		file = open(image_path, 'rb')
		image = SimpleUploadedFile(name='test_image.jpg', content=file.read(), content_type='image/jpeg')
		return image

	def setUp(self):
		self.email = 'johndoe@gmail.com'
		self.user_data = {
			'role': UserAccount.PATIENT,
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

		self.test_pic = self.create_dummy_pic()

		self.patient_profile_data = {
			'patient' : self.user,
			'patient_pic': self.test_pic,
			'gender' : 'Male',
			'dob' : timezone.now(),
			'emergency_contact_name': 'Monical Geller',
			'emergency_contact_relation': 'Friend',
			'emergency_contact_phone': '9988776655',
			'location': 'New York'
		}
		self.patient_profile = self.create_patient_profile(**self.patient_profile_data)

		self.allergy1 = self.create_allergy(name="pollen")
		self.allergy2 = self.create_allergy(name="lactose")

		self.medication1 = self.create_medication(name="gp1")
		self.medication2 = self.create_medication(name="gp2")

		self.disease1 = self.create_disease(name="Diabetes")
		self.disease2 = self.create_disease(name="Hypertension")

		self.injury1 = self.create_injury(name="Knee injury")
		self.injury2 = self.create_injury(name="Tennis elbow")

		self.surgery1 = self.create_surgery(name="Appendix")
		self.surgery1 = self.create_surgery(name="Kidney")

		self.medical_profile_data = {
			'patient' : self.patient_profile,
			'height': '5.7 ft',
			'weight': '80 kg',
			'blood_group': 'AB+',
			'allergies': [self.allergy1],
			'medications': [self.medication1],
			'past_medications': [self.medication1],
			'cronic_dieseas': [self.disease1],
			'injuries': [self.injury1],
			'surgeries': [self.surgery1]
		}

		self.patient_medical_profile = self.create_patient_medical_profile(**self.medical_profile_data)

		self.patient_lifestyle_data = {
			'patient': self.patient_profile,
			'smoking_habits': 'Regularly',
			'alchohol_consumption': 'Regularly',
			'activity_level': 'Moderate',
			'food_prefrence': 'Vegan',
			'occupation': 'Desk job',
		}
		self.patient_lifestyle = self.create_patient_lifestyle(**self.patient_lifestyle_data)

		# self.test_pic.close()


class PatientProfileTestCase(BaseTestCase):

	def test_object_created(self):
		self.assertEqual(PatientProfile.objects.count(), 1)

	def test_object_type(self):
		self.assertIsInstance(self.patient_profile, PatientProfile)

	@pytest.mark.django_db
	def test_create_object_with_empty_data(self):
		with self.assertRaises(IntegrityError):
			patient_profile = self.create_patient_profile({})

	def test_patient_field_type(self):
		self.assertIsInstance(self.patient_profile.patient)

	def test_patient_field_value(self):
		self.assertEqual(self.patient_profile.patient, self.user)

	def test_patient_pic_value(self):
		self.assertEqual(self.patient_profile.patient_pic, self.test_pic)

	def test_gender_field_value(self):
		self.assertEqual(self.patient_profile.gender, self.patient_profile_data['gender'])

	def test_dob_field_value(self):
		self.assertEqual(self.patient_profile.dob, self.patient_profile_data['dob'])

	def test_emergency_contact_name_field_value(self):
		self.assertEqual(self.patient_profile.emergency_contact_name,
						 self.patient_profile_data['emergency_contact_name'])

	def test_emergency_contact_relation_field_value(self):
		self.assertEqual(self.patient_profile.emergency_contact_relation,
						 self.patient_profile_data['emergency_contact_relation'])

	def test_emergency_contact_phone_field_value(self):
		self.assertEqual(self.patient_profile.emergency_contact_phone,
						 self.patient_profile_data['emergency_contact_phone'])

	def test_location_field_value(self):
		self.assertEqual(self.patient_profile.location,
						 self.patient_profile_data['location'])
