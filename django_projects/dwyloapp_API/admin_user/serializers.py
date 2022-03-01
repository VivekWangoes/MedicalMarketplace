from rest_framework import serializers
from accounts.models import UserAccount
from utility.send_otp_email import send_otp_email_verify


class AdminSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserAccount
        fields = ['email','name','mobile_no','role','password', 'offer']#"__all__"

    def create(self, validated_data):
        user = UserAccount.objects.create_superuser(**validated_data)
        send_otp_email_verify(user.email, user)
        return user