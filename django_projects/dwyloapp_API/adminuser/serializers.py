from rest_framework import serializers
from accounts.models import UserAccount
from accounts import views as account_view


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email','name','mobile_no','role','password']#"__all__"

    def create(self, validated_data):
        print('admin',validated_data)
        user = UserAccount.objects.create_superuser(**validated_data)
        account_view.send_otp_to_email(user.email, user)
        return user