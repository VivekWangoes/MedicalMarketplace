from rest_framework import serializers
from accounts.models import UserAccount
from utility.send_otp_email import send_otp_email_verify
from django.db import transaction
from patient.serializers import PatientProfileSerializer
from .models import *


class DoctorSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAccount
        fields = (
            'id',
            'email',
            'name',
            'mobile_no',
            'role',
            'offer',
            'term_condition'
        )


class DoctorProfileSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()

    class Meta:
        model = DoctorProfile
        fields = (
            'doctor',
            'id',
            'doctor_pic',
            'gender',
            'career_started',
            'specialty',
            'rating',
            'country',
            'state',
            'city',
            'locality',
            'clinic',
            'consultation_fees',
            'expertise_area',
            'booking_fees'
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            doctor_data = dict(validated_data.pop('doctor'))
            instance.email = doctor_data.get('email', instance.email)
            instance.name = doctor_data.get('name', instance.name)
            instance.mobile_no = doctor_data.get('mobile_no', instance.mobile_no)
            if doctor_data.get('email'):
                instance.is_email_verified = False
                send_otp_email_verify(doctor_data.get('email'), instance)
            instance.save()
            if validated_data:
                try:
                    profile_obj = DoctorProfile.objects.get(doctor=instance.id)
                    profile_obj.doctor_pic = validated_data.get('doctor_pic',profile_obj.doctor_pic)
                    profile_obj.gender = validated_data.get('gender',profile_obj.gender)
                    profile_obj.career_started = validated_data.get('career_started',
                                                                  profile_obj.career_started)
                    profile_obj.specialty = validated_data.get('specialty',profile_obj.specialty)
                    profile_obj.country = validated_data.get('country', profile_obj.country)
                    profile_obj.state = validated_data.get('state', profile_obj.state)
                    profile_obj.city = validated_data.get('city', profile_obj.city)
                    profile_obj.locality = validated_data.get('locality', profile_obj.locality)
                    profile_obj.clinic = validated_data.get('clinic',profile_obj.clinic)
                    profile_obj.consultation_fees = validated_data.get('consultation_fees',
                                                                     profile_obj.consultation_fees)
                    profile_obj.booking_fees = validated_data.get('booking_fees',
                                                                     profile_obj.booking_fees)
                    saved_expertise_area = profile_obj.expertise_area
                    if saved_expertise_area is not None:
                        saved_expertise_area = saved_expertise_area.split(',')
                    expertise_area = validated_data.get('expertise_area',profile_obj.expertise_area)
                    if expertise_area:
                        expertise_area = expertise_area.split(',')
                        if saved_expertise_area is None:
                            saved_expertise_area = ''
                        expertise_area.extend(saved_expertise_area)
                        print(saved_expertise_area,expertise_area)
                        expertise_area = set(expertise_area)
                        profile_obj.expertise_area = ','.join(expertise_area)
                    if instance.is_email_verified == True:
                        profile_obj.verification = 'Completed'
                    profile_obj.save()
                    return instance
                except:
                    return instance
            else:
                return instance


class DoctorSlotSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorSlot
        fields = '__all__'


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    time_slot = DoctorSlotSerializer(many=True)

    class Meta:
        model = DoctorAvailability
        fields = (
            'time_slot',
            'doctor',
            'slot_date',
            'day',
            'slot'
        )

   
class ConfirmAppointmentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'    


class AppointmentsSerializer(serializers.ModelSerializer):
    doctor = DoctorProfileSerializer()
    patient = PatientProfileSerializer()
    slot = DoctorSlotSerializer()

    class Meta:
        model = Appointment
        fields = (
            'id',
            'doctor',
            'patient',
            'slot',
            'status'
        )


class ConsultationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationDetail
        fields = "__all__"
    
    def update(self, instance, validated_data):
        instance.notes = validated_data.get('notes', instance.notes)
        instance.medication = validated_data.get('medication', instance.medication)
        instance.lab_test = validated_data.get('lab_test', instance.lab_test)
        instance.next_appointment = validated_data.get('next_appointment')
        instance.health_status = validated_data.get('health_status', instance.health_status)
        instance.save()
        return instance


class ConsultationDetailSerializer(serializers.ModelSerializer):
    appointment = AppointmentsSerializer()
    next_appointment = AppointmentsSerializer()
    class Meta:
        model = ConsultationDetail
        fields = (
            'id',
            'appointment',
            'notes',
            'medication',
            'lab_test',
            'next_appointment',
            'health_status'
        )


class DoctorReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DoctorReview
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.prescription_rating = validated_data.get('prescription_rating',
                                                          instance.prescription_rating)
        instance.explanation_rating = validated_data.get('explanation_rating',
                                                         instance.explanation_rating)
        instance.friendliness_rating = validated_data.get('friendliness_rating',
                                                          instance.friendliness_rating)
        instance.save()
        return instance