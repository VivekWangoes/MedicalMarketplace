from django.shortcuts import render
from .serializers import  PatientSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from project.config.messages import Messages
from cerberus import Validator
from .models import PatientProfile, Allergy, Medication, Disease, Injury,\
      Surgery, PatientMedicalProfile, PatientLifeStyle
from django.db import transaction
from .serializers import PatientProfileSerializer, PatientMedicalProfileSerializer,\
     PatientLifeStyleSerializer, AllergySerializer, MedicationSerializer,\
     DiseaseSerializer, InjurySerializer, SurgerySerializer
from .permissions import IsPatient, IsTokenValid
from accounts.models import UserAccount
from project.utility.send_otp_email import send_otp_to_email
# Create your views here.


class PatientRegister(APIView):
    """This class is used for Patient register """
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            schema = {
                    "email": {'type':'string', 'required': True, 'empty': False},
                    "name": {'type':'string', 'required': True, 'empty': False},
                    "mobile_no": {'type':'string', 'required': True, 'empty': False},
                    "password": {'type':'string', 'required': True, 'empty': False},
                    "patient_profile": {'type':'dict', 'required': False, 'empty': True},
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error':v.errors},
                                 status=status.HTTP_400_BAD_REQUEST)
            patient_profile = request.data.get('patient_profile',{})
            with transaction.atomic():
                user_obj = UserAccount.objects.create_user(email=request.data.get('email'),
                                                           name=request.data.get('name'),
                                                           mobile_no=request.data.get('mobile_no'),
                                                           password=request.data.get('password'),
                                                           role=UserAccount.PATIENT)
                user_obj.save()
                patient_profile_obj = PatientProfile.objects.create(patient=user_obj,
                                                                    gender=patient_profile.get('gender'),
                                                                    dob=patient_profile.get('dob'),
                                                                    emergency_contact_name=patient_profile.get('emergency_contact_name'),
                                                                    emergency_contact_relation=patient_profile.get('emergency_contact_relation'),
                                                                    emergency_contact_phone=patient_profile.get('emergency_contact_phone'),
                                                                    location=patient_profile.get('expertise_area'))
                patient_profile_obj.save()
                medical_profile = PatientMedicalProfile.objects.create(patient=patient_profile_obj)
                medical_profile.save()
                life_style_obj = PatientLifeStyle.objects.create(patient=patient_profile_obj)
                life_style_obj.save()
                send_otp_to_email(user_obj.email, user_obj)
            return Response({'message': Messages.ACCOUNT_CREATED},
                             status = status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status = status.HTTP_500_INTERNAL_SERVER_ERROR)

class PatientProfileView(APIView):
    """patient personal profile update"""
    permission_classes = [IsPatient, IsAuthenticated]
    def get(self, request):
        serialize_data = PatientProfileSerializer(request.user.patient_profile)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            serialize_data = PatientProfileSerializer(instance=request.user,
                                                      data=request.data,
                                                      partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()           
            return Response({'message':Messages.PROFILE_UPDATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllergyView(APIView):
    """Get all Allergy"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        allergy_data = Allergy.objects.all()
        serialize_data = AllergySerializer(alergies_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class MedicationView(APIView):
    """Get all Medication"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        medication_data = Medication.objects.all()
        serialize_data = MedicationSerializer(medication_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class DiseaseView(APIView):
    """Get all Disease"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        disease_data = Disease.objects.all()
        serialize_data = DiseaseSerializer(disease_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class InjuryView(APIView):
    """Get all Injury"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        injury_data = Injury.objects.all()
        serialize_data = InjurySerializer(injury_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class SurgeryView(APIView):
    """Get all surgery"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        surgery_data = Surgery.objects.all()
        serialize_data = SurgerySerializer(surgery_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class PatientMedicalProfileView(APIView):
    """patient medical profile update"""
    permission_classes = [IsPatient, IsAuthenticated]
    def get(self, request):
        serialize_data = PatientMedicalProfileSerializer(request.user.patient_profile.patient_medical_profile)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            serialize_data = PatientMedicalProfileSerializer(
                             instance=request.user.patient_profile.patient_medical_profile,
                             data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                patient_obj = serialize_data.save()
            #import pdb; pdb.set_trace()
            if request.data.get('alergies_data', ''):
                ids = request.data.get('alergies_data').get('id',[])
                alergy_obj = Allergy.objects.filter(name=request.data.get('alergies_data').get('new') if request.data.get('alergies_data').get('new') else [None, ]).first()
                ids.append(alergy_obj.id) if alergy_obj else None
                alergies_obj = Allergy.objects.filter(id__in=ids)
                patient_obj.alergies.set(alergies_obj)
                if not alergy_obj:
                    patient_obj.alergies.create(name=request.data.get('alergies_data')['new'])
            else:
                alergies_obj = Allergy.objects.filter(id__in=[None, ])
                patient_obj.alergies.set(alergies_obj)
            medication_obj = Medication.objects.filter(id__in=request.data.get('medication_data')  if request.data.get('medication_data') else [None, ])
            patient_obj.medication.set(medication_obj)
            dieseas_obj = Dieseas.objects.filter(id__in=request.data.get('dieseas_data') if request.data.get('dieseas_data') else [None, ])
            patient_obj.cronic_dieseas.set(dieseas_obj)
            injury_obj = injury.objects.filter(id__in=request.data.get('injuries_data') if request.data.get('injuries_data') else [None, ])
            patient_obj.injuries.set(injuries_obj)
            surgery_obj = Surgery.objects.filter(id__in=request.data.get('surgery_data') if request.data.get('surgery_data') else [None, ])
            patient_obj.surgeries.set(surgery_obj)      
            return Response({'message':Messages.PROFILE_UPDATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientLifeStyleView(APIView):
    """patient life style profile update"""
    permission_classes = [IsPatient, IsAuthenticated]
    def get(self, request):
        serialize_data = PatientLifeStyleSerializer(request.user.patient_profile.patient_life_style)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def put(self, request):
        try:
            serialize_data = PatientLifeStyleSerializer(instance=request.user.patient_profile.patient_life_style,
                                                        data=request.data,
                                                        partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()           
            return Response({'message':Messages.PROFILE_UPDATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)

