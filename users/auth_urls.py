from django.urls import path

from .views import (
    LogoutAPIView,
    OAuthLoginView,
)

app_name = "auth"

urlpatterns = [
    path("login/<str:provider>/", OAuthLoginView.as_view(), name="oauth-login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
