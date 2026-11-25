import json
import logging
import os
import re

from django.db import transaction

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

from assessment.models import AssessmentCapture, FileUpload, Assessment, Question, Choice
from assessment.apis.rag import retrieve_resume_context
from assessment.llm_prompts import ASSESSMENT_CREATION_TEMPLATE
from assessment.serializers.assessment import AssessmentSerializer

logger = logging.getLogger(__name__)


class CreateAssessmentUsingGroq(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        # 1. Automatically get the latest resume uploaded by this user.
        resume_obj = FileUpload.objects.filter(
            created_by=request.user
        ).order_by("-id").first()

        if not resume_obj:
            return Response(
                {"error": "Please upload a resume before generating an assessment."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # 2. Retrieve resume context using RAG.
            resume_context = retrieve_resume_context(
                resume_id=resume_obj.id,
                query=(
                    "Identify the candidate's programming languages, "
                    "technical skills, frameworks, projects and work experience."
                ),
                top_k=5
            )

            if not resume_context:
                return Response(
                    {"error": "Unable to retrieve resume information."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            resume_content = "\n\n".join(
                item["text"] for item in resume_context
            )

            # 3. Prepare the prompt.
            prompt = PromptTemplate(
                input_variables=["resume_content"],
                template=ASSESSMENT_CREATION_TEMPLATE["prompt"]
            )

            # 4. Initialize Groq.
            api_key = os.getenv("GROQ_API_KEY")

            if not api_key:
                raise ValueError("GROQ_API_KEY is not configured.")

            llm = ChatGroq(
                model="openai/gpt-oss-120b",
                api_key=api_key,
                temperature=0.3
            )

            chain = prompt | llm

            # 5. Generate assessment.
            response = chain.invoke({
                "resume_content": resume_content
            })

            generated_text = response.content

            # 6. Remove Markdown code fences, if present.
            generated_text = generated_text.strip()
            generated_text = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                generated_text,
                flags=re.IGNORECASE
            )

            # 7. Parse generated JSON.
            generated_data = json.loads(generated_text)

            assessment_name = generated_data["assessment_name"]
            assessment_description = generated_data["assessment_description"]
            questions = generated_data["questions"]

            if not isinstance(questions, list) or len(questions) != 5:
                raise ValueError("Groq must generate exactly five questions.")

            # 8. Save everything in the database.
            with transaction.atomic():

                assessment_obj = Assessment.objects.create(
                    resume=resume_obj,
                    name=assessment_name,
                    description=assessment_description,
                    created_by=request.user
                )

                for qn_no, question_data in enumerate(questions, start=1):

                    question_obj = Question.objects.create(
                        assessment=assessment_obj,
                        text=question_data["question"],
                        qn_no=qn_no
                    )

                    for choice_data in question_data["choices"]:

                        Choice.objects.create(
                            question=question_obj,
                            text=choice_data["text"],
                            is_correct=choice_data["is_correct"]
                        )

            # 9. Return success.
            return Response(
                {
                    "message": "Assessment generated successfully.",
                    "data": {
                        "assessment_id": assessment_obj.id,
                        "assessment_name": assessment_obj.name,
                        "assessment_description": assessment_obj.description,
                        "total_questions": len(questions)
                    }
                },
                status=status.HTTP_201_CREATED
            )

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            logger.exception("Invalid assessment response from Groq.")

            return Response(
                {"error": "Groq generated an invalid assessment. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception:
            logger.exception("Assessment generation failed.")

            return Response(
                {"error": "Unable to generate assessment."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetAssessment(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request,*args, **kwargs):

        assessment_obj = Assessment.objects.filter(
            created_by=request.user
        ).prefetch_related(
            "question_set__choice_set"
        )


        if not assessment_obj.exists():
            return Response(
                {"error": "No assessments found for this user."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AssessmentSerializer(assessment_obj, many=True)

        return Response(
            {
                "message": "Assessments retrieved successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class SaveAssessmentResponse(APIView):
    
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        assessment_id = request.data.get("assessment_id")
        responses = request.data.get("responses")

        if not assessment_id or not isinstance(responses, list):
            return Response(
                {"error": "Assessment ID and responses are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        assessment = Assessment.objects.filter(
            id=assessment_id
        ).first()

        if not assessment:
            return Response(
                {"error": "Assessment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        total_score = 0

        try:
            with transaction.atomic():

                for item in responses:

                    question = Question.objects.filter(
                        id=item.get("question_id"),
                        assessment=assessment
                    ).first()

                    if not question:
                        return Response(
                            {"error": "Invalid question ID."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    choice = Choice.objects.filter(
                        id=item.get("selected_choice_id"),
                        question=question
                    ).first()

                    if not choice:
                        return Response(
                            {"error": "Invalid choice ID."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    score = 1 if choice.is_correct else 0

                    capture = AssessmentCapture.objects.create(
                        assessment=assessment,
                        candidate=request.user,
                        question=question,
                        score=score,
                        is_attempted=True
                    )

                    capture.selected_choices.set([choice])

                    total_score += score

            return Response(
                {
                    "message": "Responses saved successfully.",
                    "total_questions": len(responses),
                    "score": total_score
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )