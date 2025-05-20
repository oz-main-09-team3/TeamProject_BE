from django.urls import path

from apps.diary.views import (
    CommentDeleteView,
    CommentLikeView,
    CommentView,
    DiaryByDateView,
    DiaryCalendarView,
    DiaryImageView,
    DiaryView,
    LikeView,
)

urlpatterns = [
    path("", DiaryView.as_view()),
    path("<int:diary_id>/", DiaryView.as_view()),
    # 달력형 일기 목록 조회
    path("calendar/", DiaryCalendarView.as_view()),
    # 특정 날짜의 일기 목록 조회
    path("date/<str:date>/", DiaryByDateView.as_view()),
    path("<int:diary_id>/comments/", CommentView.as_view()),  # 댓글 목록/작성
    path(
        "<int:diary_id>/comments/<int:comment_id>/", CommentDeleteView.as_view()
    ),  # 댓글 삭제
    path(
        "<int:diary_id>/comments/<int:comment_id>/", CommentDeleteView.as_view()
    ),  # 댓글 수정
    path("<int:diary_id>/like/", LikeView.as_view()),  # 좋아요 추가/삭제
    path("<int:diary_id>/images/", DiaryImageView.as_view()),  # 이미지 업로드/조회
    path(
        "<int:diary_id>/comments/<int:comment_id>/like/", CommentLikeView.as_view()
    ),  # 댓글 좋아요 추가/삭제
]
