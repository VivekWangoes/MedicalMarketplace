from rest_framework import serializers
from accounts.models import UserAccount
from utility.send_otp_email import send_otp_email_verify
from django.db import transaction
from .models import *


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'name', 'mobile_no', 'role', 'offer', 'term_condition']


class PatientProfileSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()

    class Meta:
        model = PatientProfile
        fields = (
            'patient',
            'id',
            'patient_pic',
            'gender',
            'dob',
            'emergency_contact_name',
            'emergency_contact_relation',
            'emergency_contact_phone',
            'location',
        )

    def update(self, instance, validated_data):
        patient_data = validated_data.pop('patient',{})
        instance.email = patient_data.get('email', instance.email)
        instance.name = patient_data.get('name', instance.name)
        instance.mobile_no = patient_data.get('mobile_no', instance.mobile_no)
        if patient_data.get('email'):
            instance.is_email_verified = False
            send_otp_email_verify(patient_data.get('email'), instance)
        instance.save()
        if validated_data:
            try:
                profile_obj = PatientProfile.objects.get(patient=instance.id)
                profile_obj.patient_pic = validated_data.get('patient_pic',profile_obj.patient_pic)
                profile_obj.gender = validated_data.get('gender',profile_obj.gender)
                profile_obj.dob = validated_data.get('dob', profile_obj.dob)
                profile_obj.emergency_contact_name = validated_data.get('emergency_contact_name',
                                                                        profile_obj.emergency_contact_name)
                profile_obj.emergency_contact_relation = validated_data.get('emergency_contact_relation',
                                                                            profile_obj.emergency_contact_relation)
                profile_obj.emergency_contact_phone = validated_data.get('emergency_contact_phone',
                                                                         profile_obj.emergency_contact_phone)
                profile_obj.location = validated_data.get('location',profile_obj.location)
                profile_obj.save()
                return instance
            except:
                return instance
        return instance


class AllergySerializer(serializers.ModelSerializer):

    class Meta:
        model = Allergy
        fields = "__all__"


class MedicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medication
        fields = "__all__"


class DiseaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Disease
        fields = "__all__"


class InjurySerializer(serializers.ModelSerializer):

    class Meta:
        model = Injury
        fields = "__all__"


class SurgerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Surgery
        fields = "__all__"


class PatientMedicalProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientMedicalProfile
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.height = validated_data.get('height', instance.height)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.blood_group = validated_data.get('blood_group', instance.blood_group)
        instance.save()
        print("#######", validated_data.get('blood_group', instance.blood_group))
        return instance


class PatientLifeStyleSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatientLifeStyle
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.smoking_habits = validated_data.get('smoking_habits', instance.smoking_habits)
        instance.alchohol_consumption = validated_data.get('alchohol_consumption', instance.alchohol_consumption)
        instance.activity_level = validated_data.get('activity_level', instance.activity_level)
        instance.food_prefrence = validated_data.get('food_prefrence', instance.food_prefrence)
        instance.occupation = validated_data.get('occupation', instance.occupation)
        instance.save()
        return instance


class PatientCompleteProfileSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    patient_medical_profile = PatientMedicalProfileSerializer()
    patient_life_style = PatientLifeStyleSerializer()

    class Meta:
        model  = PatientProfile
        fields = (
            'patient',
            'patient_medical_profile',
            'patient_life_style',
            'patient_pic',
            'gender',
            'dob',
            'emergency_contact_name',
            'emergency_contact_relation',
            'emergency_contact_phone',
            'location'
        )


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = "__all__"


class MedicineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Medicine
        fields = "__all__"


class LabTestSerializer(serializers.ModelSerializer):

    class Meta:
        model = LabTest
        fields = "__all__"


class MyCartSerializer(serializers.ModelSerializer):
    #patient = PatientProfileSerializer()

    class Meta:
        model = MyCart
        fields = "__all__"#['patient']


class MyCartItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyCartItem
        fields = "__all__"


class GetMyCartItemSerializer(serializers.ModelSerializer):
    mycart = MyCartSerializer()
    #address = AddressSerializer()
    medicine = MedicineSerializer()
    lab_test = LabTestSerializer()

    class Meta:
        model = MyCartItem
        fields = (
            "mycart",
            #"address",
            "medicine",
            "lab_test",
            "quantity",
            "prescription"
        )


class OrderSummarySerializer(serializers.ModelSerializer):
    mycart = MyCartSerializer()
    address = AddressSerializer()
    medicine = MedicineSerializer()
    lab_test = LabTestSerializer()

    class Meta:
        model = MyCartItem
        fields = (
            "mycart",
            "address",
            "medicine",
            "lab_test",
            "quantity",
            "prescription"
        )


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = "__all__"


class MyCouponSerializer(serializers.ModelSerializer):
    #patient_coupon = PatientProfileSerializer()
    coupon = CouponSerializer()

    class Meta:
        model = MyCoupon
        fields = (
            #"patient_coupon",
            "coupon",
            "coupon_code",
            "is_used"
        )