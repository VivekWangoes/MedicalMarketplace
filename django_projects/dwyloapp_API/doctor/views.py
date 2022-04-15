from django.shortcuts import render
from django.db import transaction
from datetime import datetime

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from cerberus import Validator

from utility.send_otp_email import send_otp_email_verify
from config.messages import Messages
from accounts.models import UserAccount
from .permissions import IsDoctor, IsTokenValid
from .serializers import *
from .models import *
# Create your views here.


class DoctorRegister(APIView):
    """This class is used for Doctor register"""
    permission_classes = [AllowAny,]

    def post(self, request):
        try:
            schema = {
                    "email": {'type':'string', 'required': True, 'empty': False},
                    "name": {'type':'string', 'required': True, 'empty': False},
                    "mobile_no": {'type':'string', 'required': True, 'empty': False},
                    "password": {'type':'string', 'required': True, 'empty': False},
                    "offer": {'type':'string', 'required': False, 'empty': True},
                    "booking_fees": {'type':'string', 'required': False, 'empty': True},
                    "doctor_profile": {'type':'dict', 'required': False, 'empty': True},
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error':v.errors},
                                 status=status.HTTP_400_BAD_REQUEST)
            doctor_profile = request.data.get('doctor_profile',{})
            with transaction.atomic():
                user_obj = UserAccount.objects.create_user(email=request.data.get('email'),
                                                           name=request.data.get('name'),
                                                           mobile_no=request.data.get('mobile_no'),
                                                           password=request.data.get('password'),
                                                           role=UserAccount.DOCTOR,
                                                           offer=request.data.get('offer', False),
                                                           term_condition=True)
                user_obj.save()
                doctor_profile_obj = DoctorProfile.objects.create(doctor=user_obj,
                                                                  doctor_pic=doctor_profile.get('doctor_pic'),
                                                                  gender=doctor_profile.get('gender'),
                                                                  career_started=doctor_profile.get('career_started'),
                                                                  specialty=doctor_profile.get('specialty'),
                                                                  country=doctor_profile.get('country'),
                                                                  state=doctor_profile.get('state'),
                                                                  city=doctor_profile.get('city'),
                                                                  locality=doctor_profile.get('locality'),
                                                                  clinic=doctor_profile.get('clinic'),
                                                                  consultation_fees=doctor_profile.get('consultation_fees'),
                                                                  expertise_area=doctor_profile.get('expertise_area'),
                                                                  booking_fees=doctor_profile.get('booking_fees'))
                doctor_profile_obj.save()
                send_otp_email_verify(user_obj.email, user_obj)
                return Response({'message': Messages.ACCOUNT_CREATED},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorProfileView(APIView):
    """This class is used for get and update doctor profile"""
    permission_classes = [IsDoctor, IsTokenValid]

    def get(self, request):
        try:
            serialize_data = DoctorProfileSerializer(request.user.doctor_profile)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            serialize_data = DoctorProfileSerializer(instance=request.user,
                                                     data=request.data,
                                                     partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()           
            return Response({'message':Messages.PROFILE_UPDATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            with transaction.atomic():
                doctor_obj = DoctorProfile.objects.get(doctor=request.user)
                expertise_area = request.data.get('expertise_area').split(',')
                saved_expertise_area = (doctor_obj.expertise_area).split(',')
                for area in expertise_area:
                    if area in saved_expertise_area:
                        saved_expertise_area.remove(area)
                doctor_obj.expertise_area = ','.join(saved_expertise_area)
                doctor_obj.save()
                return Response({'message': Messages.INFO_DELETED},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorAvailabilitySet(APIView):
    """This class is used for set doctor availability"""
    permission_classes = [IsDoctor, IsTokenValid]

    def post(self,request):
        try:
            schema = {
                    "slot_date": {'type': 'string', 'required': True, 'empty': False},
                    "day": {'type': 'string', 'required': True, 'empty': False},
                    "slot": {'type': 'string', 'required': True, 'empty': False},
                    "slot_time": {'type': 'list', 'required': True, 'empty': False},
                }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error': v.errors},
                                 status=status.HTTP_400_BAD_REQUEST )
            slots = DoctorAvailability.objects.filter(doctor=request.user.doctor_profile,
                                                      slot_date=request.data.get('slot_date')).\
                                                      filter(time_slot__slot_time__in=request.data.get('slot_time'))
            if slots:
                return Response({'message': Messages.DATETIME_ALREADY_PRESENT},
                                 status=status.HTTP_409_CONFLICT) 
            with transaction.atomic():
                for slot in request.data.get('slot_time'):
                    current_time  = datetime.now()
                    set_time = datetime.strptime(slot,"%Y-%m-%d %H:%M:%S")
                    if set_time <= current_time:
                        return Response({'message': Messages.INVALID_TIME},
                                 status=status.HTTP_400_BAD_REQUEST)
                    doctor_slot = DoctorSlot.objects.create(slot_time=slot)
                    doctor_slot.save()
                    available = DoctorAvailability.objects.create(doctor=request.user.doctor_profile,
                                                                  slot_date=request.data.get('slot_date'),
                                                                  day=request.data.get('day'),
                                                                  slot=request.data.get('slot'))
                    available.save()
                    available.time_slot.add(doctor_slot)
            return Response({'message': Messages.AVAILABILITY_SET},
                             status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpcomingAppointments(APIView):
    """for getting upcoming appointments"""
    permission_classes = [IsDoctor, IsTokenValid]

    def get(self, request):
        try:
            appointment_data = Appointment.objects.filter(doctor=request.user.doctor_profile,
                                                          status="UPCOMING")
            serialize_data = AppointmentsSerializer(appointment_data, many=True).data
            if not serialize_data:
                return Response({"message": Messages.NO_UPCOMING_APPOINTMENT},
                                 status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CompletedAppointments(APIView):
    """for getting upcoming appointments"""
    permission_classes = [IsDoctor, IsTokenValid]

    def get(self, request):
        try:
            appointment_data = Appointment.objects.filter(doctor=request.user.doctor_profile,
                                                          status="COMPLETED")
            serialize_data = AppointmentsSerializer(appointment_data, many=True).data
            if not serialize_data:
                return Response({"message": Messages.NO_COMPLETED_APPOINTMENT},
                                 status=status.HTTP_404_NOT_FOUND)
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorAllReview(APIView):
    """get all review by doctor"""
    permission_classes = [IsDoctor, IsTokenValid]

    def get(self, request):
        try:
            review_data  = DoctorReview.objects.filter(doctor=request.user.doctor_profile.id)
            if not review_data:
                return Response({"message":Messages.REVIEW_NOT_AVAILABLE},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = DoctorReviewsSerializer(review_data, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConsultationDetailView(APIView):
    """Give consultation detail given by doctor"""
    permission_classes = [IsDoctor, IsTokenValid]

    def get(self, request):
        try:
            consultation_data = ConsultationDetail.objects.filter(appointment__id=request.data.get('appointment_id')).first()
            if not consultation_data:
                return Response({"message":Messages.CONSULTAION_NOT_GIVEN},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = ConsultationDetailSerializer(consultation_data).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            request.data._mutable = True
            schema = {
                "appointment_id": {"type": "string", "required":True, "empty": False},
                "notes": {"type": "string", "required": False, "empty": True},
                "medication": {"type": "string", "required": False, "empty": True},
                "lab_test": {"type": "string", "required": False, "empty": True},
                "next_appointment": {"type": "string", "required": False, "empty": True}, 
                "health_status": {"type": "string", "required": False, "empty": True},
                "patient_profile_id": {"type": "string", "required": True, "empty": False}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({"error": v.errors},status=status.HTTP_400_BAD_REQUEST)
            consultation_data = ConsultationDetail.objects.filter(appointment__id=request.data.get('appointment_id'),
                                                                  appointment__status="COMPLETED").first()
                                                                                            
            if consultation_data:
                return Response({"message": Messages.CONSULTATION_ALREADY_EXIST},
                                 status=status.HTTP_208_ALREADY_REPORTED)
            if request.data.get('next_appointment'):
                patient_profile_obj = PatientProfile.objects.filter(id=request.data.get('patient_profile_id')).first()
                if not patient_profile_obj:
                    return Response({"message": Messages.PATIENT_NOT_EXIST})
                slot_time_obj = DoctorAvailability.objects.filter(doctor=request.user.doctor_profile,
                                                                  time_slot__slot_time=request.data.get('next_appointment'),
                                                                  time_slot__is_booked=True)
                if slot_time_obj:
                    return Response({"message": Messages.SLOT_ALREADY_BOOKED},
                                     status=status.HTTP_208_ALREADY_REPORTED)
                slot_obj = DoctorSlot.objects.filter(doctoravailability__doctor=request.user.doctor_profile,
                                                     doctoravailability__time_slot__slot_time=request.data.get('next_appointment'),
                                                     doctoravailability__time_slot__is_booked=False).first()
                if not slot_obj:
                    return Response({"message": Messages.SLOT_NOT_AVAILABLE},
                                     status=status.HTTP_404_NOT_FOUND)
                with transaction.atomic():
                    appointment_obj = Appointment.objects.create(doctor=request.user.doctor_profile, patient=patient_profile_obj, 
                                               slot=slot_obj, status="UPCOMING")
                    appointment_obj.save()
                    slot_obj.is_booked = True
                    slot_obj.save()
                    request.data['next_appointment'] = appointment_obj.id
            request.data['appointment'] = request.data.get('appointment_id')
            request.data._mutable = False
            serialize_data = ConsultationSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
                return Response({"message": Messages.CONSULTATION_DETAIL},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            schema = {
                "appointment_id": {"type": "string", "required":True, "empty": False},
                "notes": {"type": "string", "required": False, "empty": True},
                "medication": {"type": "string", "required": False, "empty": True},
                "lab_test": {"type": "string", "required": False, "empty": True},
                "next_appointment": {"type": "string", "required": False, "empty": True}, 
                "health_status": {"type": "string", "required": False, "empty": True},
                "patient_profile_id": {"type": "string", "required": True, "empty": False}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({"error": v.errors},status=status.HTTP_400_BAD_REQUEST)
            consultation_data = ConsultationDetail.objects.filter(appointment__id=request.data.get('appointment_id')).first()
            if not consultation_data:
                return Response({"message":Messages.CONSULTAION_NOT_GIVEN},
                                 status=status.HTTP_404_NOT_FOUND)
            previous_appointment = consultation_data.next_appointment
            request.data._mutable = True
            if previous_appointment:
                if previous_appointment.slot.slot_time and request.data.get('next_appointment'):
                    previous_appointment_time = datetime.strftime(previous_appointment.slot.slot_time,"%Y-%m-%d %H:%M:%S")
                    previous_appointment_time = datetime.strptime(previous_appointment_time,"%Y-%m-%d %H:%M:%S")
                    if previous_appointment_time == datetime.strptime(request.data.get('next_appointment'),"%Y-%m-%d %H:%M:%S"):
                        return Response({"message":Messages.SAME_SLOT_TIME}, status=status.HTTP_208_ALREADY_REPORTED)
            if request.data.get('next_appointment'):
                patient_profile_obj = PatientProfile.objects.filter(id=request.data.get('patient_profile_id')).first()
                if not patient_profile_obj:
                    return Response({"message": Messages.PATIENT_NOT_EXIST})
                slot_time_obj = DoctorAvailability.objects.filter(doctor=request.user.doctor_profile,
                                                                  time_slot__slot_time=request.data.get('next_appointment'),
                                                                  time_slot__is_booked=True)
                if slot_time_obj:
                    return Response({"message": Messages.SLOT_ALREADY_BOOKED},
                                     status=status.HTTP_208_ALREADY_REPORTED)
                slot_available_obj = DoctorSlot.objects.filter(doctoravailability__doctor=request.user.doctor_profile,
                                                               doctoravailability__time_slot__slot_time=request.data.get('next_appointment'),
                                                               doctoravailability__time_slot__is_booked=False).first()
                if not slot_available_obj:
                    return Response({"message": Messages.SLOT_NOT_AVAILABLE},
                                     status=status.HTTP_404_NOT_FOUND)
                with transaction.atomic():
                    if not previous_appointment:
                        new_appointment_obj = Appointment.objects.create(doctor=request.user.doctor_profile, patient=patient_profile_obj, 
                                                   slot=slot_available_obj, status="UPCOMING")
                        new_appointment_obj.save()
                        slot_available_obj.is_booked = True
                        slot_available_obj.save()
                        request.data['next_appointment'] = new_appointment_obj.id
                    if previous_appointment:
                        previous_appointment.slot.is_booked = False
                        previous_appointment.slot.save()
                        previous_appointment.slot = slot_available_obj
                        previous_appointment.save()
                        slot_available_obj.is_booked = True
                        slot_available_obj.save()
                        request.data['next_appointment'] = previous_appointment.id 
            request.data._mutable = False
            serialize_data = ConsultationSerializer(instance=consultation_data,
                                                    data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
                return Response({"message": Messages.CONSULTATION_UPDATE},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

