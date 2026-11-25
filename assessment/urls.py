from django.urls import path
from assessment.apis import file
from assessment.apis import assessment
from assessment.apis.adminuser import GetAllCandidateMarks

urlpatterns = [
    path('file/upload/', file.FileUploadView.as_view(), name='file-upload'),
    path('assessment/create/', assessment.CreateAssessmentUsingGroq.as_view(), name='create-assessment'),
    path('assessment/list/', assessment.GetAssessment.as_view(), name='list-assessments'),
    path('assessment/save_response/', assessment.SaveAssessmentResponse.as_view(), name='save-assessments'),
    path("admin/candidate-marks/",GetAllCandidateMarks.as_view(),name="candidate-marks"),
]