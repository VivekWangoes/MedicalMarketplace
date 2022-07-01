from django.shortcuts import render
from django.db import transaction

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from cerberus import Validator

from config.messages import Messages
from accounts.models import UserAccount
from .serializers import AdminSerializer
# Create your views here.


class AdminRegister(APIView):
    """This class is used for Admin register """
    permission_classes = [AllowAny,]

    def post(self,request):
        try:
            with transaction.atomic():
                schema = {
                        "email": {'type':'string', 'required': True, 'empty': False},
                        "name": {'type':'string', 'required': True, 'empty': False},
                        "mobile_no": {'type':'string', 'required': True, 'empty': False},
                        "password": {'type':'string', 'required': True, 'empty': False},
                        "offer": {'type':'string', 'required': False, 'empty': True},
                }
                v = Validator()
                if not v.validate(request.data, schema):
                    return Response({'error':v.errors}, 
                                     status=status.HTTP_400_BAD_REQUEST)
                request.data._mutable = True
                request.data['role'] = UserAccount.SUPER_ADMIN
                request.data['offer'] = request.data.get('offer', False)
                request.data['term_condition'] = True 
                request.data._mutable = False
                serialize_data =  AdminSerializer(data=request.data)
                if serialize_data.is_valid(raise_exception=True):
                    serialize_data.save()
                return Response({'message': Messages.ACCOUNT_CREATED},
                                 status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)