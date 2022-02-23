from django.core.mail import send_mail
from project.settings.dev import EMAIL_HOST_USER
from django_otp.oath import totp
from django_otp.util import random_hex
from rest_framework.response import Response
from rest_framework import status
import time
from django.utils import timezone
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
def send_otp_email_verify(email, user_obj):
    try:
        while(True):
            secret_key = random_hex(20)
            secret_key = secret_key.encode('utf-8')
            now = int(time.time())
            otp = totp(key=secret_key, step=30, digits=5, t0=(now))
            if len(str(otp)) == 5:
                break
        user_obj.email_otp = otp
        # current_time = timezone.now()
        user_obj.email_otp_created = datetime.utcnow()
        user_obj.save()
        # send_mail("OTP","Your One Time Password is {}".format(otp),
        #           EMAIL_HOST_USER,[email,])
        context = {'otp': otp}
        html_content = render_to_string('account/verify_email_otp.html', context)

        email = EmailMultiAlternatives('Verify Email', 'Verify your Email',
                                        EMAIL_HOST_USER, [email,])
        email.attach_alternative(html_content, 'text/html')
        email.send()
        return True
    except Exception as exception:
        return Response({"error": str(exception)},
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_otp_login(email, user_obj):
    try:
        while(True):
            secret_key = random_hex(20)
            secret_key = secret_key.encode('utf-8')
            now = int(time.time())
            otp = totp(key=secret_key, step=30, digits=5, t0=(now))
            if len(str(otp)) == 5:
                break
        user_obj.login_otp = otp
        # current_time = timezone.now()
        user_obj.login_otp_created = datetime.utcnow()
        user_obj.save()
        # send_mail("OTP","Your One Time Password is {}".format(otp),
        #           EMAIL_HOST_USER,[email,])
        context = {'otp': otp}
        html_content = render_to_string('account/otp_login.html', context)

        email = EmailMultiAlternatives('Verify OTP', 'Verify your otp for login',
                                        EMAIL_HOST_USER, [email,])
        email.attach_alternative(html_content, 'text/html')
        email.send()
        return True
    except Exception as exception:
        return Response({"error": str(exception)},
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

