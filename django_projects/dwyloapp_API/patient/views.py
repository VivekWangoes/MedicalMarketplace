from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from project.config.messages import Messages
from cerberus import Validator
from django.db import transaction
from project.utility.send_otp_email import send_otp_email_verify
import math
from datetime import datetime, timedelta, timezone
from .permissions import IsPatient, IsTokenValid
from accounts.models import UserAccount
from .models import PatientProfile, Allergy, Medication, Disease, Injury,\
      Surgery, PatientMedicalProfile, PatientLifeStyle, Address, Medicine,\
      MyCart, MyCartItem, LabTest
from .serializers import PatientProfileSerializer, PatientMedicalProfileSerializer,\
     PatientLifeStyleSerializer, AllergySerializer, MedicationSerializer,\
     DiseaseSerializer, InjurySerializer, SurgerySerializer, PatientCompleteProfileSerializer,\
     AddressSerializer, MyCartItemSerializer, GetMyCartItemSerializer, MedicineSerializer, MyCartSerializer,\
     LabTestSerializer
from doctor.models import DoctorProfile, DoctorAvailability, DoctorSlot,\
     DoctorReview, Appointment#ConsultationDetail,
from doctor.serializers import DoctorProfileSerializer, DoctorAvailabilitySerializer,\
     ConfirmAppointmentsSerializer, AppointmentsSerializer, DoctorReviewsSerializer,\
     ConsultationSerializer, ConsultationDetailSerializer
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
                    "offer": {'type':'string', 'required': False, 'empty': True},
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
                send_otp_email_verify(user_obj.email, user_obj)
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
                if alergy_obj:
                    patient_obj.alergies.create(name=request.data.get('alergies_data')['new'])
            else:
                alergies_obj = Allergy.objects.filter(id__in=[None, ])
                patient_obj.alergies.set(alergies_obj)
            medication_obj = Medication.objects.filter(id__in=request.data.get('medication_data')  if request.data.get('medication_data') else [None, ])
            patient_obj.medication.set(medication_obj)
            dieseas_obj = Disease.objects.filter(id__in=request.data.get('dieseas_data') if request.data.get('dieseas_data') else [None, ])
            patient_obj.cronic_dieseas.set(dieseas_obj)
            injury_obj = Injury.objects.filter(id__in=request.data.get('injuries_data') if request.data.get('injuries_data') else [None, ])
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

class PatientCompleteProfile(APIView):
    """patient complete profile update"""
    permission_classes = [IsPatient, IsAuthenticated]
    def get(self, request):
        serialize_data = PatientCompleteProfileSerializer(request.user.patient_profile).data
        patient_profile = [key for key in serialize_data if serialize_data[key] is not None]
        patient = dict(serialize_data['patient'])
        patient = [key for key in patient if patient[key] is not None]
        medical_profile = dict(serialize_data['patient_medical_profile'])
        medical_profile = [key for key in medical_profile if medical_profile[key] is not None and medical_profile[key]]
        life_style = dict(serialize_data['patient_life_style'])
        life_style = [key for key in life_style if life_style[key] is not None]
        complete_fields = (len(patient_profile)-3) + (len(patient)-1) + (len(medical_profile)-4) + (len(life_style)-4) 
        percentage = math.ceil((complete_fields / 25) * 100)
        serialize_data['complete_profile'] = str(percentage) + "%"
        return Response(serialize_data, status=status.HTTP_200_OK)


class DoctorSearchBySpecialty(APIView):
    """This class is used for return Doctor based on speciality"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            doctor_data = DoctorProfile.objects.filter(
                        specialty__iexact=request.data.get('specialty'))
            serialize_data = DoctorProfileSerializer(doctor_data, many=True).data
            serialize_data1 = serialize_data
            next_availability = {}
            for count, data in enumerate(serialize_data):
                doctor_user = UserAccount.objects.get(email=data['doctor']['email'])
                slots = DoctorSlot.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
                                                   slot_time__gte=datetime.utcnow(),
                                                   is_booked=False).order_by('slot_time')
                
                if slots:
                    serialize_data1[count]['next_availability'] = slots[0].slot_time
                else:
                    serialize_data1[count]['next_availability'] = "No slots available"
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctorSearchByClinic(APIView):
    """This class is used for return Doctor based on clinic"""
    permission_classes = [IsPatient,IsTokenValid]
    def get(self, request):
        try:
            doctor_data = DoctorProfile.objects.filter(
                        clinic__icontains=request.data.get('clinic'))
            serialize_data = DoctorProfileSerializer(doctor_data, many=True).data
            serialize_data1 = serialize_data
            next_availability = {}
            for count, data in enumerate(serialize_data):
                doctor_user = UserAccount.objects.get(email=data['doctor']['email'])
                slots = DoctorSlot.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
                                                   slot_time__gte=datetime.utcnow(),
                                                   is_booked=False).order_by('slot_time')
                
                if slots:
                    serialize_data1[count]['next_availability'] = slots[0].slot_time
                else:
                    serialize_data1[count]['next_availability'] = "No slots available"
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorSearchByHealthConcern(APIView):
    """This class is used for return Doctor based on HealthConcern"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            doctor_data = DoctorProfile.objects.all().filter(
                        expertise_area__icontains=request.data.get('health_concern'))
            serialize_data = DoctorProfileSerializer(doctor_data, many=True).data
            serialize_data1 = serialize_data
            next_availability = {}
            for count, data in enumerate(serialize_data):
                doctor_user = UserAccount.objects.get(email=data['doctor']['email'])
                slots = DoctorSlot.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
                                                   slot_time__gte=datetime.utcnow(),
                                                   is_booked=False).order_by('slot_time')
                
                if slots:
                    serialize_data1[count]['next_availability'] = slots[0].slot_time
                else:
                    serialize_data1[count]['next_availability'] = "No slots available"
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorSearchByDoctors(APIView):
    """This class is used for return Doctor based on Doctors"""
    permission_classes = [IsPatient,IsTokenValid]
    def get(self, request):
        try:
            doctor_data = DoctorProfile.objects.filter(doctor__name__icontains=request.data.get('name'))
            serialize_data = DoctorProfileSerializer(doctor_data, many=True).data
            serialize_data1 = serialize_data
            next_availability = {}
            for count, data in enumerate(serialize_data):
                doctor_user = UserAccount.objects.get(email=data['doctor']['email'])
                slots = DoctorSlot.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
                                                   slot_time__gte=datetime.utcnow(),
                                                   is_booked=False).order_by('slot_time')
                
                if slots:
                    serialize_data1[count]['next_availability'] = slots[0].slot_time
                else:
                    serialize_data1[count]['next_availability'] = "No slots available"
            return Response(serialize_data, status=status.HTTP_200_OK)

        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorAvailabilityProfile(APIView):
    """for getting particular doctor availabilities"""
    permission_classes = [IsPatient, IsTokenValid]
    def post(self, request):
        try:
            doctor_profile_obj = DoctorProfile.objects.filter(doctor__id=request.data.get('doctor_id')).first()
            if not doctor_profile_obj:
                return Response({"message": Messages.USER_NOT_EXISTS},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = DoctorProfileSerializer(doctor_profile_obj).data
            serialize_data1 = serialize_data
            today_slots = DoctorAvailability.objects.filter(doctor=doctor_profile_obj,
                                                            time_slot__slot_time__date=datetime.utcnow().date(),
                                                            time_slot__slot_time__gte=datetime.utcnow(),
                                                            time_slot__is_booked=False).order_by('time_slot__slot_time')
            
            serialize_data1['today_availability'] = DoctorAvailabilitySerializer(today_slots, many=True).data
            total_review = DoctorReview.objects.filter(doctor=doctor_profile_obj).count()
            if total_review:
                total_friendliness_rating = DoctorReview.objects.filter(friendliness_rating__gte="3",
                                                                        doctor=doctor_profile_obj).count()
                friendliness_rating  = (total_friendliness_rating/total_review) * 100
                serialize_data1['friendliness_rating'] = friendliness_rating
                total_review = DoctorReview.objects.filter(doctor=doctor_profile_obj).count()
                total_explanation_rating = DoctorReview.objects.filter(explanation_rating__gte="3",
                                                                       doctor=doctor_profile_obj).count()
                explanation_rating  = (total_explanation_rating/total_review) * 100
                serialize_data1['explanation_rating'] = explanation_rating
                serialize_data1['recommended_by'] = (doctor_profile_obj.rating) * 20
                recent_review = {}
                review_obj = DoctorReview.objects.filter(doctor=doctor_profile_obj).order_by('-created_at')
                recent_review['review'] = review_obj[0].review
                recent_review['name'] = review_obj[0].patient.patient.name
                serialize_data1['recent_review'] = recent_review
            return Response(serialize_data, status=status.HTTP_200_OK)

        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorAvailabilityTimeSlot(APIView):
    """for search  particular doctor slots """
    permission_classes = [IsPatient, IsTokenValid]
    def post(self, request):
        try:
            doctor_data = DoctorProfile.objects.filter(doctor__id=request.data.get('doctor_id')).first()
            if not doctor_data:
                return Response({"message": Messages.USER_NOT_EXISTS},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = DoctorProfileSerializer(doctor_data).data
            serialize_data1 = serialize_data
            date = request.data.get('date')
            if not date:
                today_slots = DoctorAvailability.objects.filter(doctor=doctor_data,
                                                                time_slot__slot_time__date=datetime.utcnow().date(),
                                                                time_slot__slot_time__gte=datetime.utcnow(),
                                                                time_slot__is_booked=False).order_by('time_slot__slot_time')
                serialize_data1['today_availability'] = DoctorAvailabilitySerializer(today_slots, many=True).data
            else:
                today_slots = DoctorAvailability.objects.filter(doctor=doctor_data,
                                                                time_slot__slot_time__date=datetime(datetime.utcnow().year,
                                                                                                    datetime.utcnow().month, int(date), tzinfo=timezone.utc),
                                                                time_slot__is_booked=False).order_by('time_slot__slot_time')
                serialize_data1['today_availability'] = DoctorAvailabilitySerializer(today_slots, many=True).data

            return Response(serialize_data, status=status.HTTP_200_OK)

        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmAppointmentsView(APIView):
    """for saving confirm appointments details"""
    permission_classes = [IsPatient, IsTokenValid]
    def post(self, request):
        try:
            appointment_obj = Appointment.objects.filter(slot__id=request.data.get('slot_id')).first()
            if appointment_obj:
                return Response({"message": Messages.SLOT_ALREADY_BOOKED},
                                 status=status.HTTP_208_ALREADY_REPORTED)
            slot_obj = DoctorSlot.objects.get(id=request.data.get('slot_id'))
            request.data._mutable = True
            request.data['doctor'] = request.data.get('doctor_id')#doctor_obj.doctor_profile.id
            request.data['patient'] = request.user.patient_profile.id
            request.data['slot'] = slot_obj.id
            request.data['status'] = 'UPCOMING'
            request.data._mutable = True
            with transaction.atomic():
                serialize_data = ConfirmAppointmentsSerializer(data=request.data)
                if serialize_data.is_valid(raise_exception=True):
                    serialize_data.save()
                    slot_obj.is_booked = True
                    slot_obj.save()
                    return Response({"message": Messages.APPOINTMENT_CONFIRMED},
                                     status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpcomingAppointments(APIView):
    """for getting upcoming appointments"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            appointment_data = Appointment.objects.filter(patient=request.user.patient_profile,
                                                          status="UPCOMING")
            serialize_data = AppointmentsSerializer(appointment_data, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompletedAppointments(APIView):
    """for getting upcoming appointments"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            appointment_data = Appointment.objects.filter(patient=request.user.patient_profile,
                                                          status="COMPLETED")
            serialize_data = AppointmentsSerializer(appointment_data, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancleAppointment(APIView):
    """for cancle appointment"""
    permission_classes = [IsPatient, IsTokenValid]
    def post(self, request, id):
        try:
            appointment_obj = Appointment.objects.filter(id=id, status='UPCOMING').first()
            if appointment_obj:
                appointment_obj.status = "CANCLE"
                appointment_obj.save()
                slot_obj = appointment_obj.slot
                slot_obj.is_booked = False
                slot_obj.save()
            else:
                return Response({"message":Messages.APPOINTMENT_NOT_EXIST}, status=status.HTTP_404_NOT_FOUND)
            return Response({"message":Messages.APPOINTMENT_CANCLE}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorReviewView(APIView):
    """write review by patient to doctor"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            review_data  = DoctorReview.objects.filter(patient=request.user.patient_profile.id)
            serialize_data = DoctorReviewsSerializer(review_data, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            request.data._mutable = True
            doctor_profile_obj = DoctorProfile.objects.filter(id=request.data.get('doctor_id')).first()
            if not doctor_profile_obj:
                return Response({"message":Messages.USER_NOT_EXISTS}, status=status.HTTP_404_NOT_FOUND)
            patient_profile_obj = DoctorReview.objects.filter(patient=request.user.patient_profile.id).first()
            if patient_profile_obj:
                return Response({"message":Messages.ALREADY_WRITTEN}, status=status.HTTP_208_ALREADY_REPORTED)
            request.data['doctor'] = doctor_profile_obj.id
            request.data['patient'] = request.user.patient_profile.id
            request.data._mutable = False
            serialize_data = DoctorReviewsSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                review_obj = serialize_data.save()
                total_rating = int(review_obj.prescription_rating) + int(review_obj.explanation_rating)\
                             + int(review_obj.friendliness_rating) 
                avg_rating = total_rating // 3
                avg_rating = (doctor_profile_obj.rating+avg_rating) / 2
                doctor_profile_obj.rating = avg_rating
                doctor_profile_obj.save()
                return Response({"message":Messages.REVIEW_SAVED}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            review_obj = DoctorReview.objects.filter(id=request.data.get('review_id')).first()
            if not review_obj:
                return Response({"message":Messages.USER_NOT_EXISTS}, status=status.HTTP_404_NOT_FOUND)
            serialize_data = DoctorReviewsSerializer(instance=review_obj,
                                                     data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
                serialize_data = serialize_data.data
                doctor_profile_obj = DoctorProfile.objects.filter(id=request.data.get('doctor_id')).first()
                if not doctor_profile_obj:
                    return Response({"message":Messages.USER_NOT_EXISTS}, status=status.HTTP_404_NOT_FOUND)
                total_rating = int(serialize_data['prescription_rating']) + int(serialize_data['explanation_rating'])\
                             + int(serialize_data['friendliness_rating']) 
                avg_rating = total_rating // 3
                avg_rating = (doctor_profile_obj.rating+avg_rating) / 2
                doctor_profile_obj.rating = avg_rating
                doctor_profile_obj.save()
                return Response({"message":Messages.REVIEW_UPDATE}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           


class PatientConsultationDetail(APIView):
    """access consultation details"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request, id):
        try:
            appointment_data = ConsultationDetail.objects.get(appointment__id=id)
            serialize_data = ConsultationDetailSerializer(appointment_data)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddressView(APIView):
    """get and post address"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            address_data = Address.objects.filter(patient=request.user.patient_profile)
            if not address_data:
                return Response({"message": Messages.ADDRESS_NOT_FOUND},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = AddressSerializer(address_data, many=True)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            schema = {
                    "house_no_building_name": {'type':'string', 'required': True, 'empty': False},
                    "street_addr1": {'type':'string', 'required': True, 'empty': False},
                    "street_addr2": {'type':'string', 'required': True, 'empty': False},
                    "pincode": {'type':'string', 'required': True, 'empty': False},
                    "mobile_no": {'type':'string', 'required': True, 'empty': False},
                    "address_type": {'type':'string', 'required': True, 'empty': False},
                    "other": {'type':'string', 'required': False, 'empty': True},
            }
            if request.data.get('other'):
                other = {
                         "name": {'type':'string', 'required': True, 'empty': False},
                         "email": {'type':'string', 'required': True, 'empty': False}
                }
                schema.update(other)

            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error':v.errors},
                                 status=status.HTTP_400_BAD_REQUEST)
            request.data._mutable = True
            request.data['patient'] = request.user.patient_profile.id
            request.data._mutable = False
            serialize_data = AddressSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
            return Response({"message": Messages.ADDRESS_SAVED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MedicineView(APIView):
    """get all medicines"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            medicine_data = Medicine.objects.filter(name__icontains=request.data['name'])
            if not medicine_data:
                return Response({"message": Messages.NO_MEDICINE},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = MedicineSerializer(medicine_data, many=True)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LabTestView(APIView):
    """get all lab tests"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            lab_test_data = LabTest.objects.filter(name__icontains=request.data['name'])
            if not lab_test_data:
                return Response({"message": Messages.LAB_TEST},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = LabTestSerializer(lab_test_data, many=True)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MyCartItemView(APIView):
    """Add Item to cart"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            mycartitem_obj = MyCartItem.objects.filter(mycart__patient_cart=request.user.patient_profile)
            print(mycartitem_obj)
            #mycartitem_obj = MyCart.objects.filter(mycartitem__mycart=MyCart.objects.filter(patient_cart=request.user.patient_profile).first())
            if not mycartitem_obj.exists():
                return Response({"message": Messages.CARTITEM_NOT_EXIST},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = GetMyCartItemSerializer(mycartitem_obj, many=True)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            mycart_obj = MyCart.objects.filter(patient_cart=request.user.patient_profile).first()
            if not mycart_obj:
                mycart_obj = MyCart.objects.create(patient_cart=request.user.patient_profile)
                mycart_obj.save()
            if request.data.get('item_choice') == "MEDICINE":
                mycart_item_obj = MyCartItem.objects.filter(medicine=request.data.get('medicine'),
                                                            mycart=mycart_obj).first()
            else:
                mycart_item_obj = MyCartItem.objects.filter(lab_test=request.data.get('lab_test'),
                                                            mycart=mycart_obj).first()
            if mycart_item_obj:
                mycart_item_obj.quantity += int(request.data.get('quantity'))
                mycart_item_obj.save()
                print(mycart_item_obj.quantity)
                return Response({"message": Messages.CART_ITEM_SAVED},
                             status=status.HTTP_200_OK)
            request.data._mutable = True
            request.data['mycart'] = mycart_obj.id
            request.data._mutable = False
            serialize_data = MyCartItemSerializer(data=request.data)
           
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
            return Response({"message": Messages.CART_ITEM_SAVED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        if request.data.get('medicine'):
            mycart_item_obj = MyCartItem.objects.filter(medicine=request.data.get('medicine'),
                                                        mycart__patient_cart=request.user.patient_profile)
            if not mycart_item_obj.exists():
                return Response({"message": Messages.CARTITEM_NOT_EXIST},
                                 status=status.HTTP_404_NOT_FOUND)
        if request.data.get('lab_test'):
            mycart_item_obj = MyCartItem.objects.filter(lab_test=request.data.get('lab_test'),
                                                        mycart__patient_cart=request.user.patient_profile)
            if not mycart_item_obj.exists():
                return Response({"message": Messages.CARTITEM_NOT_EXIST},
                                 status=status.HTTP_404_NOT_FOUND)
        if int(mycart_item_obj.first().quantity) == 1:
            mycart_obj = MyCartItem.objects.filter(mycart__patient_cart=request.user.patient_profile).first()
            mycart_obj.delete()
            return Response({"message": Messages.CART_ITEM_DELETED},
                             status=status.HTTP_404_NOT_FOUND)
        mycart_item_obj = mycart_item_obj.first()
        mycart_item_obj.quantity -= 1
        mycart_item_obj.save()
        return Response({"message": Messages.CART_ITEM_QUANTITY_DECREASED},
                         status=status.HTTP_200_OK)
