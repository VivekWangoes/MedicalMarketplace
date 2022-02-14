from django.shortcuts import render
from .serializers import AdminSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.

class AdminRegister(APIView):
    """This class is used for Admin register """
    permission_classes = [AllowAny]
    def post(self,request):
        request.data._mutable = True
        request.data['role'] = 0
        request.data._mutable = False
        print(request.data)
        serialize_data =  AdminSerializer(data=request.data)
        if serialize_data.is_valid(raise_exception=True):
            user = serialize_data.save()
        return Response({'msg':"Admin {} created successful".format(user.name)})