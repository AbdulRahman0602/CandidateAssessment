from django.db import models
from user_management.models import User
from django.utils import timezone

class FileUpload(models.Model):
    file = models.FileField(upload_to='resumes/')
    created_by = models.ForeignKey('user_management.User', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)


class Assessment(models.Model):
    resume = models.ForeignKey(FileUpload, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    text = models.TextField()
    qn_no = models.PositiveIntegerField(default=1) 

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class AssessmentCapture(models.Model):
    assessment = models.ForeignKey("Assessment", on_delete=models.CASCADE, related_name="assessment_attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name="attempts")
    selected_choices = models.ManyToManyField(Choice, blank=True)
    score = models.IntegerField(default=0)
    is_attempted = models.BooleanField(default=False)
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
    )
    

