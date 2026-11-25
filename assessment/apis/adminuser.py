from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from assessment.models import AssessmentCapture


class GetAllCandidateMarks(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        captures = AssessmentCapture.objects.select_related(
            "candidate",
            "assessment",
            "question"
        ).prefetch_related(
            "selected_choices"
        )

        results = defaultdict(lambda: {
            "candidate_id": None,
            "candidate": None,
            "assessment_id": None,
            "assessment_name": None,
            "total_questions": 0,
            "total_marks": 0,
            "responses": []
        })

        for capture in captures:

            key = (
                capture.candidate_id,
                capture.assessment_id
            )

            result = results[key]

            result["candidate_id"] = capture.candidate_id
            result["candidate"] = str(capture.candidate)
            result["assessment_id"] = capture.assessment_id
            result["assessment_name"] = capture.assessment.name

            result["total_questions"] += 1
            result["total_marks"] += capture.score

            result["responses"].append({
                "question_id": capture.question_id,
                "question": capture.question.text,
                "score": capture.score,
                "selected_choices": [
                    choice.text
                    for choice in capture.selected_choices.all()
                ]
            })

        return Response(
            {
                "message": "Candidate marks retrieved successfully.",
                "data": list(results.values())
            },
            status=status.HTTP_200_OK
        )