from rest_framework.permissions import BasePermission
from accounts.models import BlackListedToken

class IsTokenValid(BasePermission):
    def has_permission(self, request, view):
        user_id = request.user.id
        is_allowed_user = True
        token = request.auth.decode("utf-8")
        try:
            is_blackListed = BlackListedToken.objects.get(user=user_id, token=token)
            if is_blackListed:
                is_allowed_user = False
        except BlackListedToken.DoesNotExist:
            is_allowed_user = True
        return is_allowed_user

class IsDoctor(BasePermission):
	"""Check requested user is doctor or not"""
	def has_permission(self, request, view):
		try:
			user_role = request.user.role
			print('user_role', user_role)
			if user_role == 1:
				return True
			else:
				False
		except:
			False

class IsPatient(BasePermission):
	"""Check requested user is patient or not"""
	def has_permission(self, request, view):
		try:
			user_role = request.user.role
			if user_role == 2:
				return True
			else:
				False
		except:
			False
	