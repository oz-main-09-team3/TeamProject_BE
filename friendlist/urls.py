from django.urls import path

from .views import (
    FriendDeleteAPIView,
    FriendListAPIView,
)

urlpatterns = [
    # 친구 목록 조회: GET  /api/friends/?status=…
    path("", FriendListAPIView.as_view(), name="friend-list"),
    # 친구 삭제:      DELETE /api/friends/<int:friend_id>/
    path("<int:friend_id>/", FriendDeleteAPIView.as_view(), name="friend-delete"),
]
