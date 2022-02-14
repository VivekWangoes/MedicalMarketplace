from django.shortcuts import render
from django.contrib.auth import login,logout, authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from project.settings.dev import EMAIL_HOST_USER
from django_otp.oath import totp
from django_otp.util import random_hex
import time
from rest_framework_jwt.settings import api_settings
from .models import UserAccount,BlackListedToken, ContactSupport
from .permissions import IsTokenValid,IsDoctor,IsPatient
from .serializers import ContactSupportSerializer
from datetime import datetime
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from rest_framework import status
from cerberus import Validator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator 
from django.urls import reverse
from project.config import messages as Messages
from django.contrib.auth.hashers import make_password
from django.contrib import messages
# Create your views here.

def send_otp_to_email(email, user_obj):
    try:
        while(True):
            secret_key = random_hex(20)
            secret_key = secret_key.encode('utf-8')
            print('secret_key',secret_key)
            now = int(time.time())
            otp = totp(key=secret_key, step=30, digits=5, t0=(now))
            print('totp',otp)
            if len(str(otp)) == 5:
                break
        user_obj.otp = otp
        current_time = timezone.now()
        user_obj.otp_created = current_time
        user_obj.save()
        send_mail("OTP","Your One Time Password is {}".format(otp),EMAIL_HOST_USER,[email,])
        print('email sent',EMAIL_HOST_USER,email)
        return True
    except Exception as exception:
        return Response({"error": str(exception)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class VerifyEmail(APIView):
    """This class is used for verify email"""
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            print('verifyemail',request.data.get('otp'))
            #current_time = datetime.now()
            current_time = timezone.now()
            user_obj = UserAccount.objects.get(otp=request.data.get('otp'))
            otp = request.data.get('otp')
            print(user_obj.otp_created,current_time)
            time_delta = (current_time - user_obj.otp_created)
            total_seconds = time_delta.total_seconds()
            minutes = total_seconds/60
            print(minutes,type(minutes))
            if minutes > 10:
                user_obj.otp = None
                user_obj.save()
                return Response({'status':status.HTTP_400_BAD_REQUEST, 'error':"your time is expired Please again generate otp"})

            if user_obj.is_email_verified == True:
                return Response({'status':status.HTTP_200_OK, 'msg':"your email is already verified"})
            
            if user_obj.otp == otp:
                user_obj.is_email_verified = True
                user_obj.save()
                return Response({'status':status.HTTP_200_OK, 'msg':"your email is verified"})
            else:
                return Response({'status':status.HTTP_400_BAD_REQUEST,'error': 'your  otp is  wrong'})
        except Exception as e:
            return Response({'status':status.HTTP_400_BAD_REQUEST,'error': ' Your otp is wrong please check'})


    def patch(self, request):
        try:
            user_obj = UserAccount.objects.filter(email=request.data.get('email'))
            if not user_obj.exists():
                return Response({'status':400, 'error':"no user found"})
            status = send_otp_to_email(request.data.get('email'), user_obj[0])
            return Response({'status':200, 'msg':"new otp sent"})
        except Exception as exception:
            print(e)
            return Response({"error": str(exception)},status=status.HTTP_404_NOT_FOUND)



class LoginWithOTP(APIView):
    """This class is used for  login with otp"""
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user_obj = UserAccount.objects.get(otp=request.data.get('otp'))
            otp = request.data.get('otp')
            print(user_obj.email,user_obj.password)
            if user_obj.is_email_verified == True:
                current_time = timezone.now()
                print(user_obj.otp_created,current_time)
                time_delta = (current_time - user_obj.otp_created)
                total_seconds = time_delta.total_seconds()
                minutes = total_seconds/60
                print(minutes,type(minutes))
                if minutes > 10:
                    user_obj.otp = None
                    return Response({'status':404, 'error':"your time is expired Please again generate otp"})
                if user_obj.otp == otp:
                    # refresh = RefreshToken.for_user(user_obj)
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

                    payload = jwt_payload_handler(user_obj)
                    token = jwt_encode_handler(payload)
                    return Response({'msg':'UserAccount LoggedIn','id':user_obj.id, 'user':str(user_obj),'role':user_obj.role,'token':token})
                
                else:
                    return Response({'status':404,'error': 'your  otp is  wrong'})
            
            else:
                return Response({'status':406,'error': 'First verify your email'})
        except:
            return Response({'status':404,'error': 'your  otp is  wrong'})


class SignIn(APIView):
    """This class is used for user signin"""
    permission_classes = [AllowAny]
    def post(self, request):
            email = request.data.get('email')
            password = request.data.get('password')
            try:
                user_obj = UserAccount.objects.get(email=email)
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
                        return Response({'msg':'UserAccount LoggedIn','id':user.id, 'user':str(user),'user_role':user.role,'token':token})
                        
                    else:
                        return Response({'status':404,'error': 'invalid credentials'})
                else:
                    return Response({'status':406,'error': 'First verify your email'})
            except:
                return Response({'status':400, 'error':"no user found"})


from .serializers import UserSerializer
class Users(APIView):
    permission_classes = [IsTokenValid]
    print(permission_classes)
    def get(self,request):
        user_data = UserAccount.objects.all()
        serialize_data = UserSerializer(user_data,many=True)
        #print(serialize_data)
        return Response(serialize_data.data)

         


class UserLogout(APIView):
    """This class is used for user logout"""
    def post(self,request):
        token = request.auth.decode("utf-8")
        BlackListedToken.objects.create(user=request.user, token=token)
        return Response({'status':200, "message":"user logout successfully",'token':token})


class ContactSupportQueryView(APIView):
    """This class is used for get users query"""
    permission_classes = [IsAdminUser]
    def get(self,request):
        user_data = ContactSupport.objects.all()
        serialize_data = ContactSupportSerializer(user_data,many=True)
        #print(serialize_data)
        return Response(serialize_data.data)

class ContactSupportQueryRegistered(APIView):
    """This class is used for saving users query"""
    permission_classes = [AllowAny]
    def post(self, request):
        serialize_data = ContactSupportSerializer(data=request.data)
        if serialize_data.is_valid(raise_exception=True):
            serialize_data.save()
            return Response({"Status":200, "message":"your query save" +
                        " successfull our contact team will help out with in 2 working hour"})





# from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
# import uuid
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.encoding import smart_str, force_str, smart_bytes,\
#                                  DjangoUnicodeDecodeError
# def send_forget_password_mail(email,current_site,uidb64,token):
#         print('send_forget_password_mail')
#         activate_url = 'http://{}/change_password/{}/{}/'.format(current_site,uidb64,token)
#         print(activate_url)
#         html_content = render_to_string('account/forgot_password.html', 
#                                         {'user':email,'url':activate_url})
#         message = EmailMultiAlternatives(
#                 subject='forgot password',
#                 body='welcome {}'.format(email),
#                 from_email=EMAIL_HOST_USER,
#                 to=[email]
#                 )
#         message.attach_alternative(html_content, "text/html")

#         message.send()



# @csrf_exempt
# def change_password(request,uidb64,token):
#     try:
#         if request.method == 'POST':
#             print('change_password uidb64 token',uidb64,token)
#             new_password = request.POST.get('new_password')
#             confirm_password = request.POST.get('reconfirm_password')
#             user_id = smart_str(urlsafe_base64_decode(uidb64))
#             user = UserAccount.objects.get(id=user_id)

#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({'error': 'Token is not valid, please request a new one'},\
#                                 status=status.HTTP_400_BAD_REQUEST)
#             if user_id is  None:
#                 messages.success(request, 'No user id found.')
#                 return redirect(f'/change-password/{token}/')
                
            
#             if  new_password != confirm_password:
#                 messages.success(request, 'both should  be equal.')
#                 return redirect(f'/change_password/{uidb64}/{token}/')
                         
            
#             user_obj = User.objects.get(id = user_id)
#             user_obj.set_password(new_password)
#             user_obj.save()
#             return redirect('/login/')

#     except Exception as e:
#         print(e)
#     return render(request , 'account/change_password.html')



# class ForgotPassword(APIView):
#     permission_classes = [AllowAny]
#     def post(self,request):
#         try:
#             print(request.data.get('email'))
#             user_obj = UserAccount.objects.get(email=request.data.get('email'))
#             print(user_obj)
#             uidb64 = urlsafe_base64_encode(smart_bytes(user_obj.id))
#             print('uidb64',uidb64,type(uidb64))
#             token = PasswordResetTokenGenerator().make_token(user_obj)
#             print('token',token,type(token))
#             current_site = get_current_site(request=request).domain
#             print('current_site',current_site)
#             send_forget_password_mail(user_obj.email,current_site,uidb64,token)

#             return Response({"Status":200,"success":"email sent successfull"})
#         except:
#             return Response({"Status":404,'error':"user not found"})
                

def change_password(request, uidb64=None, token=None):
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
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # Validate the request
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
                return Response({"message": Messages.EMAIL_NOT_VALID}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"error": str(exception)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
