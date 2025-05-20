from django.urls import path

from .views import (
    FriendCommentDetailView,
    FriendCommentLikeView,
    FriendCommentView,
    FriendDiaryCalendarView,
    FriendDiaryDetailView,
    FriendDiaryMonthView,
    FriendLikeView,
)

app_name = "frienddiary"

urlpatterns = [
    path(
        "<int:friend_id>/calendar/", FriendDiaryCalendarView.as_view(), name="calendar"
    ),
    path(
        "<int:friend_id>/monthdiary/",
        FriendDiaryMonthView.as_view(),
        name="month_diaries",
    ),
    path(
        "<int:friend_id>/diary/<int:diary_id>/",
        FriendDiaryDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:friend_id>/diary/<int:diary_id>/comments/",
        FriendCommentView.as_view(),
        name="comment_create",
    ),
    path(
        "<int:friend_id>/diary/<int:diary_id>/comments/<int:comment_id>/",
        FriendCommentDetailView.as_view(),
        name="comment_detail",
    ),
    path(
        "<int:friend_id>/diary/<int:diary_id>/like/",
        FriendLikeView.as_view(),
        name="diary_like",
    ),
    path(
        "<int:friend_id>/diary/<int:diary_id>/comments/<int:comment_id>/like/",
        FriendCommentLikeView.as_view(),
        name="comment_like",
    ),
]
