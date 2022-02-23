from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from accounts.models import (
	UserAccount,
	UserAccountManager,
	BlackListedToken,
	ContactSupport
)

from datetime import datetime

import pytest
import uuid


class BaseTestCase(TestCase):

	@pytest.mark.django_db
	def create_user(self, **kwargs):
		return UserAccount.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_blacklistedtoken(self, **kwargs):
		return BlackListedToken.objects.create(**kwargs)

	@pytest.mark.django_db
	def create_contactsupport(self, **kwargs):
		contactsupport = ContactSupport(**kwargs)
		contactsupport.save()
		return contactsupport

	def setUp(self):
		# import pdb; pdb.set_trace()
		self.user_data = {
			'role': UserAccount.DOCTOR,
			'email': 'johndoe@gmail.com',
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

		self.blacklistedtoken_data = {
			'token' : Token.generate_key(),
			'user' : self.user,
		}
		self.blacklistedtoken = self.create_blacklistedtoken(**self.blacklistedtoken_data)

		self.contactsupport_data = {
			'name': 'John Doe',
			'email': 'johndoe@doeco.com',
			'description': 'Please help out regarding recent order.'
		}
		self.contactsupport = self.create_contactsupport(**self.contactsupport_data)


class UserAccountTestCase(BaseTestCase):
	def test_object_created(self):
		self.assertEqual(UserAccount.objects.count(), 1)

	def test_object_created_type(self):
		self.assertIsInstance(self.user, UserAccount)

	def test_if_id_is_uuid(self):
		self.assertIsInstance(self.user.id, uuid.UUID)

	def test_role_field_value(self):
		self.assertEqual(self.user.role, UserAccount.DOCTOR)

	def test_role_field_by_updating_value(self):
		self.user.role = UserAccount.PATIENT
		self.user.save()
		self.assertEqual(self.user.role, UserAccount.PATIENT)

	def test_role_field_value_with_nonexistent_choice(self):
		self.user.role = 3
		with self.assertRaises(ValidationError):
			self.user.save()

	def test_email_field_value(self):
		self.assertEqual(self.user.email, self.user_data['email'])

	def test_email_field_invalid_email_format(self):
		data = self.user_data.copy()
		data['email'] = 'johndoegmail.com'
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_name_field_value(self):
		self.assertEqual(self.user.name, self.user_data['name'])

	def test_name_field_with_empty_string(self):
		data = self.user_data.copy()
		data['email'] = 'testuser@gmail.com'
		data['name'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_otp_field(self):
		self.assertEqual(self.user.otp, self.user_data['otp'])

	def test_otp_created_field(self):
		now = datetime.now()
		self.user.otp_created = now
		self.user.save()
		self.assertEqual(self.user.otp_created, now)

	def test_otp_created_field_type(self):
		now = datetime.now()
		self.user.otp_created = now
		self.user.save()
		self.assertIsInstance(self.user.otp_created, datetime)

	def test_mobile_no_field_value(self):
		self.assertEqual(self.user.mobile_no, self.user_data['mobile_no'])

	def test_mobile_no_field_with_excessive_invalid_number_length(self):
		pass

	def test_mobile_no_field_with_small_invalid_number_length(self):
		pass

	def test_mobile_no_field_with_non_numerical_value(self):
		pass

	def test_last_name_field_value(self):
		self.assertEqual(self.user.last_name, self.user_data['last_name'])

	def test_is_staff_field_value(self):
		self.assertFalse(self.user.is_staff)

	def test_is_active_field_value(self):
		self.assertTrue(self.user.is_active)

	def test_is_email_verified_field_value(self):
		self.assertFalse(self.user.is_email_verified)

	def test_device_id_field_value(self):
		self.assertEqual(self.user.device_id, self.user_data['device_id'])

	def test_status_field_default_value(self):
		self.assertEqual(self.user.status, UserAccount.ACTIVE)

	def test_status_field_value_after_updation(self):
		self.user.status = UserAccount.INACTIVE
		self.user.save()
		self.assertEqual(self.user.status, UserAccount.INACTIVE)

	def test_status_field_value_with_nonexistent_choice(self):
		self.user.status = 'INVALID_STATUS_CHOICE'
		with self.assertRaises(ValidationError):
			self.user.save()

	def test_USERNAME_FIELD_value(self):
		self.assertEqual(UserAccount.USERNAME_FIELD, 'email')

	def test_get_full_name_method(self):
		self.assertEqual(self.user.get_full_name(), self.user.name)

	def test_get_short_name(self):
		self.assertEqual(self.user.get_short_name(), self.user.name)

	def test_if_created_at_field_value_exists(self):
		self.assertTrue(self.user.created_at)

	def test_if_updated_at_field_value_exists(self):
		self.assertTrue(self.user.updated_at)


class UserAccountManagerTestCase(BaseTestCase):

	@pytest.mark.django_db
	def create_user(self, **kwargs):
		email = kwargs.get('email')
		name = kwargs.get('name')
		mobile_no = kwargs.get('mobile_no')
		password = kwargs.get('password')
		role = kwargs.get('role')
		return UserAccount.objects.create_user(email, name, mobile_no, password, role)

	@pytest.mark.django_db
	def create_superuser(self, **kwargs):
		email = kwargs.get('email')
		name = kwargs.get('name')
		mobile_no = kwargs.get('mobile_no')
		password = kwargs.get('password')
		role = kwargs.get('role')
		return UserAccount.objects.create_superuser(email, name, mobile_no, password, role)

	def setUp(self):
		super().setUp()
		self.superuser_data = self.user_data.copy()
		self.superuser_data['email'] = 'superuser@gmail.com'
		self.superuser_data['is_superuser'] = True
		self.superuser_data['is_staff'] = True

		self.superuser = self.create_superuser(**self.superuser_data)


	def test_create_user_result_with_all_correct_value(self):
		self.assertIsInstance(self.user, UserAccount)

	def test_create_user_is_active_with_all_correct_value(self):
		self.assertTrue(self.user.is_active)

	def test_create_user_with_badly_formatted_email(self):
		data = self.user_data.copy()
		data['email'] = 'johndoegmail.com'
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_create_user_with_empty_email(self):
		data = self.user_data.copy()
		data['email'] = ''
		with self.assertRaises(ValueError):
			user = self.create_user(**data)		

	def test_create_user_with_empty_mobile_number(self):
		data = self.user_data.copy()
		data['email'] = 'testemail@gmail.com'
		data['mobile_no'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_create_user_with_empty_password(self):
		data = self.user_data.copy()
		data['password'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_create_user_with_empty_role(self):
		data = self.user_data.copy()
		data['role'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	def test_create_user_with_nonexistent_role_value(self):
		data = self.user_data.copy()
		data['role'] = '4'
		with self.assertRaises(ValidationError):
			user = self.create_user(**data)

	
	def test_create_superuser_result_with_all_correct_value(self):
		self.assertIsInstance(self.superuser, UserAccount)

	def test_create_superuser_is_active_with_all_correct_value(self):
		self.assertTrue(self.superuser.is_active)

	def test_create_superuser_is_staff_with_all_correct_value(self):
		self.assertTrue(self.superuser.is_staff)

	def test_create_superuser_is_superuser_with_all_correct_value(self):
		self.assertTrue(self.superuser.is_superuser)

	def test_create_superuser_with_badly_formatted_email(self):
		data = self.superuser_data.copy()
		data['email'] = 'johndoegmail.com'
		with self.assertRaises(ValidationError):
			user = self.create_superuser(**data)

	def test_create_superuser_with_empty_email(self):
		data = self.superuser_data.copy()
		data['email'] = ''
		with self.assertRaises(ValueError):
			user = self.create_superuser(**data)

	def test_create_superuser_with_empty_mobile_number(self):
		data = self.superuser_data.copy()
		data['mobile_no'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_superuser(**data)

	def test_create_superuser_with_empty_password(self):
		data = self.superuser_data.copy()
		data['password'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_superuser(**data)

	def test_create_user_with_empty_role(self):
		data = self.superuser_data.copy()
		data['role'] = ''
		with self.assertRaises(ValidationError):
			user = self.create_superuser(**data)

	def test_create_user_with_nonexistent_role_value(self):
		data = self.superuser_data.copy()
		data['role'] = '4'
		with self.assertRaises(ValidationError):
			user = self.create_superuser(**data)


class BlackListedTokenTestCase(BaseTestCase):

	def test_object_created(self):
		self.assertTrue(self.blacklistedtoken)

	def test_object_type(self):
		self.assertIsInstance(self.blacklistedtoken, BlackListedToken)

	def test_token_field_value(self):
		self.assertEqual(self.blacklistedtoken.token, self.blacklistedtoken_data['token'])

	def test_user_field_type(self):
		self.assertIsInstance(self.blacklistedtoken.user, UserAccount)

	def test_user_field_value(self):
		self.assertEqual(self.blacklistedtoken.user, self.user)

	def test_if_timestamp_field_value_exits(self):
		self.assertTrue(self.blacklistedtoken.timestamp)

	def test_timestamp_field_value_type(self):
		self.assertIsInstance(self.blacklistedtoken.timestamp, datetime)

	def test_str_method_value(self):
		self.assertEqual(self.blacklistedtoken.__str__(), str(self.user))


class ContactSupportTestCases(BaseTestCase):

	def test_object_created(self):
		self.assertTrue(self.contactsupport)

	def test_object_type(self):
		self.assertIsInstance(self.contactsupport, ContactSupport)

	def test_name_field_value(self):
		self.assertEqual(self.contactsupport.name, self.contactsupport_data['name'])

	def test_email_field_value(self):
		self.assertEqual(self.contactsupport.email, self.contactsupport_data['email'])

	def test_description_field_value(self):
		self.assertEqual(self.contactsupport.description, self.contactsupport_data['description'])

	def test_if_created_date_field_value_exits(self):
		self.assertTrue(self.contactsupport.created_at)

	def test_str_method_value(self):
		self.assertEqual(self.contactsupport.__str__(), self.contactsupport.name)