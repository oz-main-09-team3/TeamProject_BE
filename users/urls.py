from django.urls import path

from .views import (
    UserMeAPIView,
    UserUpdateAPIView,
)

app_name = "users"

urlpatterns = [
    path("me/", UserMeAPIView.as_view(), name="user-me"),
    path("me/update/", UserUpdateAPIView.as_view(), name="user-update"),
]
