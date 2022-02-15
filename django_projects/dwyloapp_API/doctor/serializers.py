from rest_framework import serializers
from accounts.models import UserAccount
from .models import DoctorProfile, DoctorInfo, DoctorAvailability
from project.utility.send_otp_email import send_otp_to_email


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email', 'name', 'mobile_no', 'role', 'password']#"__all__"


class DoctorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorInfo
        fields = '__all__'#['clinic','consultation_fees','experties_area'] 

    def update(self, instance, validated_data):
        instance.clinic = validated_data.get('clinic',instance.clinic)
        instance.consultation_fees = validated_data.get('consultation_fees',instance.consultation_fees)
        saved_experties_area = instance.experties_area
        if saved_experties_area is not None:
            saved_experties_area = saved_experties_area.split(',')
        experties_area = validated_data.get('experties_area',instance.experties_area)
        if experties_area:
            experties_area = experties_area.split(',')
            if saved_experties_area is None:
                saved_experties_area = ''
            experties_area.extend(saved_experties_area)
            experties_area = set(experties_area)
            instance.experties_area = ','.join(experties_area)
        instance.save()
        return instance
             


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    doctor_profile = DoctorProfileSerializer()

    class Meta:
        model = UserAccount
        fields = ['doctor_profile', "name", 'email', 'mobile_no']


    def update(self,instance, validated_data):
        profile_data = dict(validated_data['doctor_profile'])
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        if validated_data.get('email'):
            instance.is_email_verified = False
            send_otp_to_email(validated_data.get('email'), instance)
        instance.save()
        if profile_data:
            try:
                user_obj = DoctorProfile.objects.get(doctor=instance.id)
                user_obj.gender = profile_data.get('gender',user_obj.gender)
                user_obj.experience = profile_data.get('experience',user_obj.experience)
                user_obj.specialty = profile_data.get('specialty',user_obj.specialty)
                user_obj.location_city = profile_data.get('location_city',user_obj.location_city)
                if instance.is_email_verified == True :
                    user_obj.verification = 'Completed'
                user_obj.save()

                return instance
            except:
                return instance
        else:
            return instance




class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = "__all__"
       

        