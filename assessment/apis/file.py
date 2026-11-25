from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from assessment.validators.file import FileUploadValidator
from assessment.serializers.file import FileUploadSerializer
from assessment.models import FileUpload
from assessment.apis.rag import process_resume

class FileUploadView(APIView):

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]  
    @swagger_auto_schema(request_body=FileUploadValidator)
    def post(self, request, *args, **kwargs):
        content={}
        serializer = FileUploadValidator(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            me = request.user

            file_obj = FileUpload.objects.create(
                file=data['file'], 
                created_by=me
                )
            rag_result = process_resume(file_obj)

            content["data"] = FileUploadSerializer(file_obj).data
            content["message"] = "File Uploaded!"
            
            return Response(content, status=status.HTTP_201_CREATED)
        content["message"] = "Invalid data"
        content["errors"] = serializer.errors
        return Response(content, status=status.HTTP_400_BAD_REQUEST)