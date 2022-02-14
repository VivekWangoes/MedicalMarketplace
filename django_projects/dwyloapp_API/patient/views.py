from django.shortcuts import render
from .serializers import  PatientSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.


class PatientRegister(APIView):
    """This class is used for Patient register """
    permission_classes = [AllowAny]
    def post(self,request):
        print(request.user)
        request.data._mutable = True
        request.data['role'] = 2
        request.data._mutable = False
        serialize_data =  PatientSerializer(data=request.data)
        if serialize_data.is_valid(raise_exception=True):
            user = serialize_data.save()
            
        return Response({'msg':"Patient {} created successful".format(user.name)})