"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    emotions. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    emotions. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls.py import include, path
    emotions. Add a URL to urlpatterns:  path('blog/', include('blog.urls.py'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps import diary
from users.views import LogoutAPIView, OAuthLoginView, UserMeAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="Emotion API",
        default_version="v1",
        description="감정 관련 API 문서입니다.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/emotions/", include("emotion.urls")),
    path(
        "api/auth/login/<str:provider>/", OAuthLoginView.as_view(), name="oauth-login"
    ),
    path("api/users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("api/diary/", include("apps.diary.urls")),
    path("api/qrcode/", include("qr.urls")),
    path("api/notifications/", include("notifications.urls")),
    # Swagger UI
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # Redoc UI (선택)
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
