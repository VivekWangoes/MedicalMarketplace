from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from accounts.models import UserAccount
from .serializers import DoctorSerializer, DoctorProfileSerializer,\
     DoctorAvailabilitySerializer, ConfirmAppointmentsSerializer, AppointmentsSerializer,\
     DoctorReviewsSerializer
from .permissions import IsDoctor, IsPatient, IsTokenValid
from .models import DoctorProfile, DoctorAvailability, DoctorSlots, Appointments, DoctorReviews
from datetime import datetime, timedelta, timezone
from cerberus import Validator
from project.config.messages import Messages
from project.utility.send_otp_email import send_otp_to_email
from django.db import IntegrityError, transaction
import calendar
# Create your views here.


class DoctorRegister(APIView):
    """This class is used for Doctor register"""
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            schema = {
                    "email": {'type':'string', 'required': True, 'empty': False},
                    "name": {'type':'string', 'required': True, 'empty': False},
                    "mobile_no": {'type':'string', 'required': True, 'empty': False},
                    "password": {'type':'string', 'required': True, 'empty': False},
                    "doctor_profile": {'type':'dict', 'required': False, 'empty': True},
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error':v.errors},
                                 status=status.HTTP_400_BAD_REQUEST)
            doctor_profile = request.data.get('doctor_profile',{})
            with transaction.atomic():
                user = UserAccount.objects.create_user(email=request.data.get('email'),
                                                       name=request.data.get('name'),
                                                       mobile_no=request.data.get('mobile_no'),
                                                       password=request.data.get('password'),
                                                       role=1)
                user.save()
                doctor_profile = DoctorProfile.objects.create(doctor=user,
                                                              gender=doctor_profile.get('gender'),
                                                              career_started=doctor_profile.get('career_started'),
                                                              specialty=doctor_profile.get('specialty'),
                                                              location_city=doctor_profile.get('location_city'),
                                                              clinic=doctor_profile.get('clinic'),
                                                              consultation_fees=doctor_profile.get('consultation_fees'),
                                                              expertise_area=doctor_profile.get('expertise_area'))
                doctor_profile.save()
                send_otp_to_email(user.email, user)
                return Response({'message': Messages.ACCOUNT_CREATED},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
                #handle_exception()
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorProfileView(APIView):
    """This class is used for get and update doctor profile"""
    permission_classes = [IsDoctor, IsTokenValid]
    def get(self, request):
        serialize_data = DoctorProfileSerializer(request.user.doctor_profile)
        return Response(serialize_data.data, status=status.HTTP_200_OK)

    def put(self, request):
        parser_classes = [FileUploadParser]
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
                                                      slot_date=request.data.get('slot_date')).filter(time_slot__slot_time__in=request.data.get('slot_time'))
            print(slots)
            if slots:
                return Response({'message': Messages.ALREADY_DATETIME_PRESENT},
                                 status=status.HTTP_409_CONFLICT) 
            with transaction.atomic():
                for slot in request.data.get('slot_time'):
                    doctor_slot = DoctorSlots.objects.create(slot_time=slot)
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
                slots = DoctorSlots.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
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
                slots = DoctorSlots.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
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
                slots = DoctorSlots.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
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
                slots = DoctorSlots.objects.filter(doctoravailability__doctor=doctor_user.doctor_profile,
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
            doctor_data = DoctorProfile.objects.get(doctor__id=request.data.get('id'))
            serialize_data = DoctorProfileSerializer(doctor_data).data
            serialize_data1 = serialize_data
            today_slots = DoctorAvailability.objects.filter(doctor=doctor_data,
                                                            time_slot__slot_time__date=datetime.utcnow().date(),
                                                            time_slot__slot_time__gte=datetime.utcnow(),
                                                            time_slot__is_booked=False).order_by('time_slot__slot_time')
            
            serialize_data1['today_availability'] = DoctorAvailabilitySerializer(today_slots, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)

        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorAvailabilityTimeSlot(APIView):
    """for search  particular doctor slots """
    permission_classes = [IsPatient, IsTokenValid]
    def post(self, request):
        try:
            doctor_data = DoctorProfile.objects.get(doctor__id=request.data.get('id'))
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
            doctor_obj = UserAccount.objects.get(id=request.data.get('doctor_id'))
            slot_obj = DoctorSlots.objects.get(id=request.data.get('slot_id'))
            request.data._mutable = True
            request.data['doctor'] = doctor_obj.doctor_profile.id
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
            appointment_data = Appointments.objects.filter(status="UPCOMING")
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
            appointment_data = Appointments.objects.filter(status="COMPLETED")
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
            appointment_obj = Appointments.objects.filter(id=id, status='UPCOMING').first()
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

class DoctorReview(APIView):
    """write review by patient to doctor"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        try:
            review_data  = DoctorReviews.objects.filter(doctor=request.data.get('doctor_id'))
            serialize_data = DoctorReviewsSerializer(review_data, many=True).data
            return Response(serialize_data, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            request.data._mutable = True
            profile_obj = DoctorProfile.objects.filter(id=request.data.get('doctor_id')).first()
            if not profile_obj:
                return Response({"message":Messages.USER_NOT_EXISTS}, status=status.HTTP_404_NOT_FOUND)
            request.data['doctor'] = profile_obj.id
            request.data['patient'] = request.user.patient_profile.id
            request.data._mutable = False
            serialize_data = DoctorReviewsSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                review_obj = serialize_data.save()
                total_rating = int(review_obj.prescription_rating) + int(review_obj.explanation_rating)\
                             + int(review_obj.friendliness_rating) 
                avg_rating = total_rating // 3
                profile_obj.rating = avg_rating
                profile_obj.save()
                return Response({"message":Messages.REVIEW_SAVED}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            review_obj = DoctorReviews.objects.filter(id=request.data.get('review_id')).first()
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
                doctor_profile_obj.rating = avg_rating
                doctor_profile_obj.save()
                return Response({"message":Messages.REVIEW_UPDATE}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
           