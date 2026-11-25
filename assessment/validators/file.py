from rest_framework import serializers
from assessment.models import FileUpload


class FileUploadValidator(serializers.Serializer):
    file = serializers.FileField()
    