
from rest_framework import serializers
from assessment.models import Assessment, Question, Choice



class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):

    choices = ChoiceSerializer(source="choice_set",many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "qn_no", "choices"]


class AssessmentSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(source="question_set",many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "resume",
            "questions"
        ]

