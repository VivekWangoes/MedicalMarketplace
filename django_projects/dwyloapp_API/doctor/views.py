from django.shortcuts import render
from django.db import transaction
from datetime import datetime

from rest_framework.permissions import IsAuthenticated,AllowAny
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
                                                                  gender=doctor_profile.get('gender'),
                                                                  career_started=doctor_profile.get('career_started'),
                                                                  specialty=doctor_profile.get('specialty'),
                                                                  location_city=doctor_profile.get('location_city'),
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

    def get(self, request, id):
        try:
            consultation_data = ConsultationDetail.objects.filter(appointment__id=id).first()
            if not consultation_data:
                return Response({"message":Messages.CONSULTAION_NOT_GIVEN},
                                 status=status.HTTP_404_NOT_FOUND)
            serialize_data = ConsultationDetailSerializer(consultation_data).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, id):
        try:
            consultation_data = ConsultationDetail.objects.filter(appointment__id=id).first()
            if consultation_data:
                return Response({"message": Messages.CONSULT_ALREADY_EXIST},
                                 status=status.HTTP_208_ALREADY_REPORTED)
            request.data._mutable = True
            request.data['appointment'] = id
            request.data._mutable = False
            serialize_data = ConsultationSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
                return Response({"message": Messages.CONSULTATION_DETAIL},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            consultation_data = ConsultationDetail.objects.get(appointment__id=id)
            serialize_data = ConsultationSerializer(instance=consultation_data,
                                                    data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
                return Response({"message": Messages.CONSULTATION_UPDATE},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

