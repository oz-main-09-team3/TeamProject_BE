from django.urls import path

from .views import FriendDeleteAPIView, FriendListAPIView

urlpatterns = [
    path("", FriendListAPIView.as_view(), name="friend-list"),
    path("<int:friend_id>/", FriendDeleteAPIView.as_view(), name="friend-delete"),
]
