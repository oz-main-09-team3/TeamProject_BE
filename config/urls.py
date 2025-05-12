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
from django.views.generic import TemplateView

from apps import diary
from users.views import LogoutAPIView, OAuthLoginView, UserMeAPIView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/emotion/", include("emotion.urls")),
    path(
        "api/auth/login/<str:provider>/", OAuthLoginView.as_view(), name="oauth-login"
    ),
    path("api/users/me/", UserMeAPIView.as_view(), name="user-me"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("api/diary/", include("apps.diary.urls")),
    path("api/qrcode/", include("qr.urls")),
    path("api/notifications/", include("notifications.urls")),
    # API-Swagger
    path("swagger/", TemplateView.as_view(template_name="swagger.html")),
]
