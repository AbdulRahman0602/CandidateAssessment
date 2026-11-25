from assessment.models import FileUpload
from rest_framework import serializers

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = "__all__"