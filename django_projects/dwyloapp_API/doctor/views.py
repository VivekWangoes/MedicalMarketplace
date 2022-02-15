from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework import status
from accounts.models import UserAccount
from .serializers import DoctorSerializer, DoctorProfileSerializer,\
                         DoctorProfileUpdateSerializer, DoctorInfoSerializer,\
                         DoctorAvailabilitySerializer
from .permissions import IsDoctor, IsPatient, IsTokenValid
from .models import DoctorProfile, DoctorInfo, DoctorAvailability
from datetime import datetime, timedelta
from cerberus import Validator
from project.config import messages as Messages
from project.utility.send_otp_email import send_otp_to_email
# Create your views here.


class DoctorRegister(APIView):
    """This class is used for Doctor register"""
    permission_classes = [AllowAny]
    def post(self,request):
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
            if not type(request.data) == dict:
                request.data._mutable = True
                request.data['role'] = 1
                request.data._mutable = False
            else:
                request.data['role'] = 1
            doctor_profile = request.data.get('doctor_profile',{})
            #serialize_data =  DoctorSerializer(data=request.data)
            user = UserAccount.objects.create_user(email=request.data.get('email'),
                                                   name=request.data.get('name'),
                                                   mobile_no=request.data.get('mobile_no'),
                                                   password=request.data.get('password'),
                                                   role=request.data.get('role'))

            doctor_profile = DoctorProfile.objects.create(doctor=user,
                                                          gender=doctor_profile.get('gender'),
                                                          experience=doctor_profile.get('experience'),
                                                          specialty=doctor_profile.get('specialty'),
                                                          location_city=doctor_profile.get('location_city'))
            doctor_info = DoctorInfo.objects.create(doctor=user, clinic=None,
                                                    consultation_fees=None,
                                                    experties_area=None)
            doctor_profile.save()
            send_otp_to_email(user.email, user)
            return Response({'message': Messages.ACCOUNT_CREATED},
                            status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorProfileUpdate(APIView):
    """This class is used for update doctor profile"""
    permission_classes = [IsDoctor, IsTokenValid]
    def get(self,request):
        doctor_data = DoctorProfile.objects.get(doctor__iexact=request.user)
        serialize_data = DoctorProfileUpdateSerializer(doctor_data)
        return Response(serialize_data.data)


    def put(self, request):
        try:
            doctor_obj = UserAccount.objects.get(email=request.user)
            serialize_data = DoctorProfileUpdateSerializer(instance=doctor_obj,
                                                           data=request.data,
                                                           partial=True)
            if serialize_data.is_valid(raise_exception=True):
                user = serialize_data.save()           
            return Response({'message':Messages.PROFILE_UPDATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DoctorInfoView(APIView):
    """This class is used for update doctor extra information"""
    permission_classes = [IsDoctor, IsTokenValid]
    def put(self, request):
        # try:
            doctor_obj = DoctorInfo.objects.get(doctor=request.user.id)
            print('request_data',request.data,doctor_obj)
            serialize_data = DoctorInfoSerializer(instance=doctor_obj,
                                                  data=request.data, partial=True)
            if serialize_data.is_valid(raise_exception=True):
                user = serialize_data.save()
            return Response({'message': Messages.INFO_UPDATED},
                             status=status.HTTP_200_OK)
        # except Exception as exception:
        #         return Response({'error': str(exception)},
        #                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DoctorAvailabilityView(APIView):
    """This class is used for set doctor availability"""
    permission_classes = [IsDoctor, IsTokenValid]
    def post(self,request):
        # try:
            months = {'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,
                        'July':7,'August':8,'September':9,'October':10,'November':11,
                        'December':12}
            request.data._mutable = True
            request.data['doctor'] = request.user.id
            year = request.data.get('year')
            month = months[request.data.get('month').title()]
            date = request.data.get('date')
            from_available = request.data.get('from_available')
            to_available = request.data.get('to_available')
            if not request.data.get('daily'):
                schema = {
                        "doctor":{'type': 'integer', 'required': True, 'empty': False},
                        "year": {'type': 'string', 'required': True, 'empty': False},
                        "month": {'type': 'string', 'required': True, 'empty': False},
                        "date": {'type': 'string', 'required': True, 'empty': False},
                        "day": {'type': 'string', 'required': True, 'empty': False},
                        "from_available": {'type': 'string', 'required': True, 'empty': False},
                        "to_available": {'type': 'string', 'required': False, 'empty': True},
                    }
                v = Validator()
                if not v.validate(request.data, schema):
                    return Response({'error': v.errors},
                                     status=status.HTTP_400_BAD_REQUEST )
                if not to_available:
                    time_str = "{}-{}-{} {}".format(year,month,date,from_available)
                    time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                    time = time + timedelta(minutes=30)
                    request.data['to_available'] = time.strftime('%I:%M %p')
                request.data._mutable = False
                time_str = "{}-{}-{} {}".format(year,month,date,from_available)
                from_time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                print('from_time=',from_time)
                time_str = "{}-{}-{} {}".format(year,month,date,request.data['to_available'])
                to_time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                print('to_time=',to_time)
                if to_time <= from_time:
                    return Response({'message': Messages.INVALID_DATETIME},
                                     status=status.HTTP_400_BAD_REQUEST)

                doctor_data = DoctorAvailability.objects.filter(doctor=request.user)
                for doctor in doctor_data:
                    if doctor.date:
                        time_str = "{}-{}-{} {}".format(year,month,date,from_available)
                        from_time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                        time_str = "{}-{}-{} {}".format(doctor.year, months[(doctor.month).title()], doctor.date,
                                 doctor.from_available)
                        saved_from_time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                        time_str = "{}-{}-{} {}".format(doctor.year, months[(doctor.month).title()], doctor.date,
                                 doctor.to_available)
                        saved_to_time = datetime.strptime(time_str, '%Y-%m-%d %I:%M %p')
                        print('saved_from_time',saved_from_time)
                        print('saved_to_time',saved_to_time)
                    else:
                        print('else')
                        time_str = "{}-{} {}".format(year,month,from_available)
                        from_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                        time_str = "{}-{} {}".format(doctor.year, months[(doctor.month).title()],
                                 doctor.from_available)
                        saved_from_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                        print('elsesaved_from_time',saved_from_time)
                        time_str = "{}-{} {}".format(doctor.year, months[(doctor.month).title()],
                                 doctor.to_available)
                        saved_to_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                        print('elsesaved_to_time',saved_to_time)
                    if from_time >= saved_from_time and from_time < saved_to_time:
                        print(saved_from_time ,from_time ,saved_to_time)
                        return Response({'message': Messages.ALREADY_DATETIME_PRESENT},
                                         status=status.HTTP_409_CONFLICT)
            else:
                print('eslse')
                schema = {
                        "doctor":{'type': 'integer', 'required': True, 'empty': False},
                        "year": {'type': 'string', 'required': True, 'empty': False},
                        "month": {'type': 'string', 'required': True, 'empty': False},
                        "from_available": {'type': 'string', 'required': True, 'empty': False},
                        "to_available": {'type': 'string', 'required': False, 'empty': True},
                        "daily": {'type':'string','required':True,'empty':False}
                    }
                
                v = Validator()
                print(request.data)
                if not v.validate(request.data, schema):
                    return Response({'error': v.errors},
                                     status=status.HTTP_400_BAD_REQUEST )
                if not to_available:
                    time_str = "{}-{} {}".format(year,month,from_available)
                    time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                    time = time + timedelta(minutes=30)
                    request.data['to_available'] = time.strftime('%I:%M %p')
                request.data._mutable = False
                time_str = "{}-{} {}".format(year,month,from_available)
                from_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                print('from_time=',from_time)
                time_str = "{}-{} {}".format(year,month,request.data['to_available'])
                to_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                print('to_time=',to_time)
                if to_time <= from_time:
                    return Response({'message': Messages.INVALID_DATETIME},
                                     status=status.HTTP_400_BAD_REQUEST)
                doctor_data = DoctorAvailability.objects.filter(doctor=request.user)
                print(doctor_data)
                for doctor in doctor_data:
                    time_str = "{}-{} {}".format(doctor.year, months[(doctor.month).title()],
                                 doctor.from_available)
                    saved_from_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                    print('saved_from_time',saved_from_time)
                    time_str = "{}-{} {}".format(doctor.year, months[(doctor.month).title()],
                                 doctor.to_available)
                    saved_to_time = datetime.strptime(time_str, '%Y-%m %I:%M %p')
                    print('saved_to_time',saved_to_time)
                    if from_time >= saved_from_time and from_time < saved_to_time:
                        print(saved_from_time ,from_time ,saved_to_time)
                        return Response({'message': Messages.ALREADY_DATETIME_PRESENT},
                                         status=status.HTTP_409_CONFLICT)

            serialize_data = DoctorAvailabilitySerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                serialize_data.save()
            return Response({'message': Messages.AVAILABILITY_SET},
                             status=status.HTTP_200_OK)

        # except Exception as exception:
        #     return Response({"error": str(exception)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DoctorSearchBySpecialty(APIView):
    """This class is used for return Doctor based on speciality"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        doctor_data = DoctorProfile.objects. filter(
                    specialty__iexact=request.data.get('specialty'))
        doctors_result = {}
        count = 1
        for doctor in doctor_data:
            temp = {}
            try:
                doctor = UserAccount.objects.get(email=doctor)
                temp['id'] = doctor.id
                temp['name'] = doctor.name
            except:
                pass
            try:
                doctor_profile_obj = DoctorProfile.objects.get(doctor=doctor)
                temp['experience'] = doctor_profile_obj.experience
                temp['specialty'] = doctor_profile_obj.specialty
                temp['location_city'] = doctor_profile_obj.location_city
            except:
                pass
            try:
                doctor_info_obj = DoctorInfo.objects.get(doctor=doctor)
                temp['clinic'] = doctor_info_obj.clinic
                temp['consultation_fees'] = doctor_info_obj.consultation_fees
            except:
                pass
            doctors_result['doctor'+str(count)] = temp
            count += 1
        return Response(doctors_result)


class DoctorSearchByClinic(APIView):
    """This class is used for return Doctor based on clinic"""
    permission_classes = [IsPatient,IsTokenValid]
    def get(self, request):
        doctor_data = DoctorInfo.objects.filter(
                    clinic__iexact=request.data.get('clinic'))
        if not doctor_data:
            doctor_data = DoctorInfo.objects.all().filter(
                        clinic__icontains=request.data.get('clinic'))
        doctors_result = {}
        count = 1
        for doctor in doctor_data:
            temp = {}
            try:
                doctor = UserAccount.objects.get(email=doctor)
                temp['id'] = doctor.id
                temp['name'] = doctor.name
            except:
                pass
            try:
                doctor_profile_obj = DoctorProfile.objects.get(doctor=doctor)
                temp['experience'] = doctor_profile_obj.experience
                temp['specialty'] = doctor_profile_obj.specialty
                temp['location_city'] = doctor_profile_obj.location_city
            except:
                pass
            try:
                doctor_info_obj = DoctorInfo.objects.get(doctor=doctor)
                temp['clinic'] = doctor_info_obj.clinic
                temp['consultation_fees'] = doctor_info_obj.consultation_fees
            except:
                pass
            doctors_result['doctor'+str(count)] = temp
            count += 1
        return Response(doctors_result)


class DoctorSearchByHealthConcern(APIView):
    """This class is used for return Doctor based on HealthConcern"""
    permission_classes = [IsPatient, IsTokenValid]
    def get(self, request):
        doctor_data = DoctorInfo.objects.all().filter(
                    experties_area__icontains=request.data.get('health_concern'))
        doctors_result = {}
        count = 1
        for doctor in doctor_data:
            temp = {}
            try:
                doctor = UserAccount.objects.get(email=doctor)
                temp['id'] = doctor.id
                temp['name'] = doctor.name
            except:
                pass
            try:
                doctor_profile_obj = DoctorProfile.objects.get(doctor=doctor)
                temp['experience'] = doctor_profile_obj.experience
                temp['specialty'] = doctor_profile_obj.specialty
                temp['location_city'] = doctor_profile_obj.location_city
            except:
                pass
            try:
                doctor_info_obj = DoctorInfo.objects.get(doctor=doctor)
                temp['clinic'] = doctor_info_obj.clinic
                temp['consultation_fees'] = doctor_info_obj.consultation_fees
            except:
                pass
            doctors_result['doctor'+str(count)] = temp
            count += 1
        return Response(doctors_result)





class DoctorSearchByDoctors(APIView):
    """This class is used for return Doctor based on Doctors"""
    permission_classes = [IsPatient,IsTokenValid]
    def get(self, request):
        doctor_data = UserAccount.objects.filter(name__iexact=request.data.get('name'))
        if not doctor_data:
            doctor_data = DoctorInfo.objects.all().filter(
                        name__icontains=request.data.get('name'))
        doctors_result = {}
        count = 1
        for doctor in doctor_data:
            temp = {}
            try:
                doctor = UserAccount.objects.get(email=doctor)
                temp['id'] = doctor.id
                temp['name'] = doctor.name
            except:
                pass
            try:
                doctor_profile_obj = DoctorProfile.objects.get(doctor=doctor)
                temp['experience'] = doctor_profile_obj.experience
                temp['specialty'] = doctor_profile_obj.specialty
                temp['location_city'] = doctor_profile_obj.location_city
            except:
                pass
            try:
                doctor_info_obj = DoctorInfo.objects.get(doctor=doctor)
                temp['clinic'] = doctor_info_obj.clinic
                temp['consultation_fees'] = doctor_info_obj.consultation_fees
            except:
                pass
            doctors_result['doctor'+str(count)] = temp
            count += 1
        return Response(doctors_result)


