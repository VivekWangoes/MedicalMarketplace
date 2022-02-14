from rest_framework import serializers
from .models import UserAccount, ContactSupport
from accounts import views


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['name','email','password','mobile_no','role']


class ContactSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactSupport
        fields = '__all__'







# class PatientPersonalProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         models = PatientPersonalProfile
#         fields = '__all__'


# class UserAccountSerializer(serializers.ModelSerializer):
    
#     personal_profile=PatientPersonalProfileSerializer()
#     class Meta:
#         model = UserAccount
#         fields = "__all__"

#     def create(self, validated_data):
#         personal_profile_data = validated_data.pop('personal_profile')
        
#         user = UserAccount.objects.create_user(**validated_data)
#         #for data in teacher_info_data:
#         PatientPersonalProfile.objects.create(patient=user, **personal_profile_data)
#         return user
    
#     def update(self, instance, validated_data):
#         instance.name = validated_data.get('name', instance.name)
#         instance.email = validated_data.get('email', instance.email)
#         password = validated_data.get('password', instance.password)
#         instance.set_password(password)
#         instance.save()
#         print(validated_data)
#         try:
#             personal_profile_data = validated_data.get('personal_profile')
            
#             personal_profile = PatientPersonalProfile.objects.get(patient=instance)
#             personal_profile.mobile_no = personal_profile_data.get('mobile_no', personal_profile.mobile_no)
#             #personal_profile.user_roll = personal_profile_data.get('user_roll', personal_profile.user_roll)
#             personal_profile.gender = personal_profile_data.get('gender', personal_profile.gender)
#             personal_profile.date_of_birth = personal_profile_data.get('date_of_birth', personal_profile.date_of_birth)
#             personal_profile.location_city = personal_profile_data.get('location_city', personal_profile.location_city)
#             personal_profile.emerg_name = personal_profile_data.get('user_roll', personal_profile.user_roll)
#             personal_profile.emerg_mobile_no = personal_profile_data.get('emerg_mobile_no', personal_profile.emerg_mobile_no)
#             personal_profile.save()
#             return instance
#         except:
#              return instance