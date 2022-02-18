from rest_framework import serializers
from accounts.models import UserAccount
from accounts.views import send_otp_to_email
from project.utility.send_otp_email import send_otp_to_email
from django.db import transaction
class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email','name','mobile_no','role','password']#"__all__"

    def create(self, validated_data):
        with transaction.atomic():
            user = UserAccount.objects.create_user(**validated_data)
            send_otp_to_email(user.email, user)
            return user
