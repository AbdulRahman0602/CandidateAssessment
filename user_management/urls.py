from django.urls import path
from user_management.api import user

urlpatterns = [
    path('signup/',user.CreateUser.as_view(),name='create_user'),
]