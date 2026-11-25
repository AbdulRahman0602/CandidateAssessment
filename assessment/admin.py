from django.contrib import admin
from assessment.models import Assessment, AssessmentCapture, Choice, FileUpload, Question

admin.site.register(FileUpload)
admin.site.register(Assessment)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(AssessmentCapture)
