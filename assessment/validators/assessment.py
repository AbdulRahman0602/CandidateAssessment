from rest_framework import serializers
from assessment.models import Assessment
from user_management.models import User
from django.utils.dateparse import parse_datetime


class CreateAssessmentValidatorUsingGroq(serializers.Serializer):
    assessment_name = serializers.CharField(max_length=100, required=True)
    assessment_description = serializers.CharField(max_length=1000, required=True)
    resume_id = serializers.IntegerField()  
    
