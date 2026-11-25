from user_management.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_management.validators.user import UserValidator
from drf_yasg.utils import swagger_auto_schema

class CreateUser(APIView):

    @swagger_auto_schema(request_body=UserValidator)
    def post(self,request,*args,**kwargs):
        content = {}
        serializer = UserValidator(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = User(
                email = data['email']
            )
            user.set_password(data['password'])
            user.save()
            content['message'] = 'User created successfully'
            return Response(content,status=status.HTTP_201_CREATED)
        else:
            content = serializer.errors
            return Response(content,status=status.HTTP_404_NOT_FOUND)


