from rest_framework import serializers
from .models import UserAccount, ContactSupport
from accounts import views


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['name','email','password','mobile_no','role']


class UserSerializerForView(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['name', 'email', 'mobile_no', 'role']


class ContactSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSupport
        fields = '__all__'


