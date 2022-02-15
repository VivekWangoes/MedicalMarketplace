from django.shortcuts import render
from .serializers import AdminSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from project.config import messages as Messages
from cerberus import Validator
# Create your views here.

class AdminRegister(APIView):
    """This class is used for Admin register """
    permission_classes = [AllowAny]
    def post(self,request):
        try:
            schema = {
                    "email": {'type':'string', 'required': True, 'empty': False},
                    "name": {'type':'string', 'required': True, 'empty': False},
                    "mobile_no": {'type':'string', 'required': True, 'empty': False},
                    "password": {'type':'string', 'required': True, 'empty': False}
            }
            v = Validator()
            if not v.validate(request.data, schema):
                return Response({'error':v.errors}, 
                                 status=status.HTTP_400_BAD_REQUEST)
            request.data._mutable = True
            request.data['role'] = 0
            request.data._mutable = False
            serialize_data =  AdminSerializer(data=request.data)
            if serialize_data.is_valid(raise_exception=True):
                user = serialize_data.save()
            return Response({'message': Messages.ACCOUNT_CREATED},
                             status=status.HTTP_200_OK)
        except Exception as exception:
                return Response({'error': str(exception)},
                                 status=status.HTTP_500_INTERNAL_SERVER_ERROR)