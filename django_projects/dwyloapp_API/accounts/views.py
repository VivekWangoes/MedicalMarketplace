from django.shortcuts import render
from django.contrib.auth import login,logout, authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
import time
from rest_framework_jwt.settings import api_settings
from .models import UserAccount,BlackListedToken, ContactSupport
from .permissions import IsTokenValid,IsDoctor,IsPatient
from .serializers import ContactSupportSerializer, UserSerializerForView
from datetime import datetime
# from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from cerberus import Validator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator 
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from project.utility.send_otp_email import send_otp_email_verify, send_otp_login
from project.config.messages import Messages
from datetime import datetime, timezone
from django.db import transaction
from project.settings.dev import EMAIL_HOST_USER

# Create your views here.
class VerifyEmail(APIView):
    """This class is used for verify email"""
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            current_time = datetime.now(timezone.utc)
            user_obj = UserAccount.objects.filter(email_otp=request.data.get('otp')).first()
            if not user_obj:
                return Response({'message': Messages.OTP_WRONG}, 
                                 status=status.HTTP_400_BAD_REQUEST)
            otp = request.data.get('otp')
            time_delta = (current_time - user_obj.email_otp_created)
            total_seconds = time_delta.total_seconds()
            minutes = total_seconds/60
            if minutes > 5:
                user_obj.email_otp = None
                user_obj.save()
                return Response({'message': Messages.OTP_TIME_EXPIRED}, 
                                 status=status.HTTP_408_REQUEST_TIMEOUT)

            if user_obj.is_email_verified == True:
                return Response({'message': Messages.ALREADY_EMAIL_VERIFIED}, 
                                 status=status.HTTP_208_ALREADY_REPORTED)
            
            with transaction.atomic():
                if user_obj.email_otp == otp:
                    user_obj.is_email_verified = True
                    user_obj.email_otp = None
                    user_obj.save()
                    return Response({'message': Messages.EMAIL_VERIFIED},
                                     status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'message': Messages.OTP_WRONG}, 
                                     status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            return Response({'error': str(exception)}, 
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            with transaction.atomic():
                email = request.data.get('email')
                user_obj = UserAccount.objects.get(email=email)
                if not user_obj:
                    return Response({'message': Messages.USER_NOT_EXISTS},
                                     status=status.HTTP_404_NOT_FOUND)
                send_otp_email_verify(email, user_obj)
                return Response({'message': Messages.OTP_SENT})
        except Exception as exception:
            return Response({'error': str(exception)}, 
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginWithOTP(APIView):
    """This class is used for  login with otp"""
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            user_obj = UserAccount.objects.filter(login_otp=request.data.get('otp')).first()
            if not user_obj:
                return Response({'message': Messages.OTP_WRONG}, status=status.HTTP_400_BAD_REQUEST)
            otp = request.data.get('otp')
            if user_obj.is_email_verified == True:
                current_time = datetime.now(timezone.utc)
                time_delta = (current_time - user_obj.login_otp_created)
                total_seconds = time_delta.total_seconds()
                minutes = total_seconds/60
                with transaction.atomic():
                    if minutes > 5:
                        user_obj.login_otp = None
                        user_obj.save()
                        return Response({'message': Messages.OTP_TIME_EXPIRED}, 
                                         status=status.HTTP_408_REQUEST_TIMEOUT)
                    if user_obj.login_otp == otp:
                        user_obj.login_otp = None
                        user_obj.save()
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user_obj)
                        token = jwt_encode_handler(payload)
                        return Response({'message': Messages.USER_LOGGED_IN, 
                                         'id': user_obj.id, 'user': str(user_obj),
                                         'role': user_obj.role,'token': token},
                                         status=status.HTTP_200_OK)
                    else:
                        return Response({'message': Messages.OTP_WRONG},
                                     status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': Messages.FIRST_VERIFY_EMAIL},
                                 status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as exception:
            return Response({'error': str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            with transaction.atomic():
                email = request.data.get('email')
                user_obj = UserAccount.objects.get(email=email)
                if not user_obj:
                    return Response({'message': Messages.USER_NOT_EXISTS},
                                     status=status.HTTP_404_NOT_FOUND)
                send_otp_login(email, user_obj)
                return Response({'message': Messages.OTP_SENT})
        except Exception as exception:
            return Response({'error': str(exception)}, 
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignIn(APIView):
    """This class is used for user signin"""
    permission_classes = [AllowAny, ]
    def post(self, request):
            email = request.data.get('email')
            password = request.data.get('password')
            try:
                user_obj = UserAccount.objects.get(email=email)
                print(user_obj)
                if user_obj.is_email_verified == True:
                    user = authenticate(email=email, password=password)
                    if user:
                        login(request, user)
                        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                        payload = jwt_payload_handler(user)
                        token = jwt_encode_handler(payload)
                        previous_tokens = BlackListedToken.objects.filter(user=user)
                        previous_tokens.delete()
                        return Response({'message': Messages.USER_LOGGED_IN, 
                                         'id': user_obj.id, 'user': str(user_obj),
                                         'role': user_obj.role,'token': token},
                                         status=status.HTTP_200_OK)
                        
                    else:
                        return Response({'message': Messages.INVALID_CREDENTIAL},
                                         status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'message': Messages.FIRST_VERIFY_EMAIL},
                                     status=status.HTTP_406_NOT_ACCEPTABLE)
            except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .serializers import UserSerializer
class UsersView(APIView):
    """For get all users"""
    #permission_classes = [IsAdminUser, IsTokenValid]
    permission_classes = [IsAdminUser]
    def get(self,request):
        user_data = UserAccount.objects.all()
        serialize_data = UserSerializerForView(user_data, many=True)
        return Response(serialize_data.data, status=status.HTTP_200_OK)


class UserLogout(APIView):
    """This class is used for user logout"""
    permission_classes = [IsAuthenticated, IsTokenValid]
    def post(self,request):
        try:
            with transaction.atomic():
                token = request.auth.decode("utf-8")
                BlackListedToken.objects.create(user=request.user, token=token)
                return Response({'message': Messages.USER_LOGGED_OUT},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactSupportQueryView(APIView):
    """
    This class is used for get users query.
    Admin can access this class
    """
    permission_classes = [IsAdminUser, ]
    def get(self,request):
        try:
            user_data = ContactSupport.objects.all()
            serialize_data = ContactSupportSerializer(user_data, many=True)
            return Response(serialize_data.data, status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactSupportQueryRegister(APIView):
    """This class is used for saving users query"""
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            with transaction.atomic():
                serialize_data = ContactSupportSerializer(data=request.data)
                if serialize_data.is_valid(raise_exception=True):
                    serialize_data.save()
                    return Response({"message": Messages.QUERY_SAVED},
                                     status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def change_password(request, uidb64=None, token=None):
    """This class is used for change password"""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserAccount.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None
    if request.method == 'POST':
        password1 = request.POST["new_password"]
        password = request.POST['reconfirm_password']
        if password == password1:
            password = make_password(password)
            UserAccount.objects.filter(pk=uid).update(password=password)
            return render(request, 'account/password_done.html')
        else:
            messages.info(request, "password not match")
            return render(request, 'account/change_password.html')
    elif user and default_token_generator.check_token(user, token):
        return render(request, 'account/change_password.html')
    else:
        return render(request, 'account/link_expired.html')


class ForgotPassword(APIView):
    """send forgot password link to user"""
    permission_classes = [AllowAny, ]
    def post(self, request):
        try:
            schema = {
                "email": {'type': 'string', 'required': True, 'empty': False}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response(
                    {'error': v.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = UserAccount.objects.filter(email=request.data.get('email'))
            if not user.exists():
                return Response({"message": Messages.EMAIL_NOT_VALID},
                                 status=status.HTTP_400_BAD_REQUEST)
            current_site = get_current_site(request)
            kwargs = {
                "uidb64": urlsafe_base64_encode(force_bytes(user.first().pk)).encode().decode(),
                "token": default_token_generator.make_token(user.first())
            }
            activation_url = reverse("accounts:change_password", kwargs=kwargs)
            activate_url = "{0}://{1}{2}".format(request.scheme,
                                                 request.get_host(), activation_url)

            context = {
                'user': user.first().name,
                'activate_url': activate_url
            }
            html_content = render_to_string('account/forgot_password.html', context)

            email = EmailMultiAlternatives('Reset password', 'Reset your password',
                                            EMAIL_HOST_USER, [user.first().email, ])
            email.attach_alternative(html_content, 'text/html')
            email.send()
            return Response({"message": Messages.LINK_SENT}, status=status.HTTP_200_OK)
        except Exception as exception:
            return Response({"error": str(exception)},
                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)
