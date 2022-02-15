from django.core.mail import send_mail
from project.settings.dev import EMAIL_HOST_USER
from django_otp.oath import totp
from django_otp.util import random_hex
from rest_framework.response import Response
from rest_framework import status
import time
from django.utils import timezone

def send_otp_to_email(email, user_obj):
    try:
        while(True):
            print('while')
            secret_key = random_hex(20)
            secret_key = secret_key.encode('utf-8')
            now = int(time.time())
            otp = totp(key=secret_key, step=30, digits=5, t0=(now))
            if len(str(otp)) == 5:
                break
        user_obj.otp = otp
        current_time = timezone.now()
        user_obj.otp_created = current_time
        user_obj.save()
        send_mail("OTP","Your One Time Password is {}".format(otp),
                  EMAIL_HOST_USER,[email,])
        return True
    except Exception as exception:
        return Response({"error": str(exception)},
                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

