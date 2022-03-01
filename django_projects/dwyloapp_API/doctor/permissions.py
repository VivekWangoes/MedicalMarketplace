from rest_framework.permissions import BasePermission
from accounts.models import BlackListedToken
from accounts.models import UserAccount


class IsTokenValid(BasePermission):
    def has_permission(self, request, view):
        is_allowed_user = True
        token = request.auth.decode("utf-8")
        try:
            is_blackListed = BlackListedToken.objects.get(user=request.user.id, token=token)
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
			if user_role == UserAccount.DOCTOR:
				return True
			else:
				False
		except:
			False
	