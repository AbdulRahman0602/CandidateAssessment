from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt import views as jwt_views

schema_view = get_schema_view(
    openapi.Info(
        title=settings.API_NAME,
        default_version='v1',
        description=settings.API_NAME,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

API_PREFIX = "api/v"+str(settings.API_VERSION)+"/"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', schema_view.with_ui('swagger',cache_timeout=0), name='schema-swagger-ui'),

    # Auth: login and get JWT
    path(API_PREFIX+'token/',
        jwt_views.TokenObtainPairView.as_view(),
        name ='token_obtain_pair'
    ),
    
    path(
        API_PREFIX+'token/refresh/',
        jwt_views.TokenRefreshView.as_view(),
        name ='token_refresh'),
    
    path(API_PREFIX+'token/logout/',
        jwt_views.TokenBlacklistView.as_view(),
        name ='logout'
    ),

    path(API_PREFIX+'user/',
        include('user_management.urls'),
    ),

    path(API_PREFIX+'assessments/',
            include('assessment.urls'),
        )
]
