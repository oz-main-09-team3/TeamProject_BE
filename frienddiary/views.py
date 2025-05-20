from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.diary.models import (
    Diary,
    DiaryEmotion,
)
from emotion.serializers import EmotionSerializer
from frienddiary.apis import (
    create_friend_comment,
    create_friend_comment_like,
    create_friend_diary_like,
    delete_friend_comment,
    delete_friend_comment_like,
    delete_friend_diary_like,
    get_friend_calendar_overview,
    get_friend_diaries_over_month,
    update_friend_comment,
)
from frienddiary.serializers import (
    CalendarDiarySerializer,
    DiaryDetailSerializer,
    DiaryListSerializer,
)
from friends.models import DiaryFriend


def _check_friend_or_terminate(user, friend_id):
    if not DiaryFriend.objects.filter(
        Q(user=user, friend_user_id=friend_id)
        | Q(user_id=friend_id, friend_user_id=user),
        status="accepted",
    ).exists():
        return False
    return True


class FriendDiaryCalendarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, friend_id):
        if not _check_friend_or_terminate(request.user, friend_id):
            return Response(
                {"message": "친구 관계가 아닙니다."}, status=status.HTTP_403_FORBIDDEN
            )

        now = datetime.now()
        year = int(request.query_params.get("year", now.year))
        month = int(request.query_params.get("month", now.month))

        calendar_data = get_friend_calendar_overview(
            request.user, friend_id, year, month
        )
        serializer = CalendarDiarySerializer(calendar_data, many=True)
        return Response(serializer.data)


class FriendDiaryMonthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, friend_id):
        """
        GET /api/friends/diaries/{friend_id}/
        → 현재 연·월의 일기 전체 목록 반환
        """
        now = datetime.now()
        year = now.year
        month = now.month

        try:
            diaries = get_friend_diaries_over_month(
                request.user, friend_id, year=year, month=month
            )
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = DiaryListSerializer(
            diaries, many=True, context={"request": request}
        )
        return Response(serializer.data)


class FriendDiaryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, friend_id, diary_id):
        if not _check_friend_or_terminate(request.user, friend_id):
            return Response(
                {"message": "친구 관계가 아닙니다."}, status=status.HTTP_403_FORBIDDEN
            )

        try:
            diary = Diary.objects.get(id=diary_id, user_id=friend_id, is_deleted=False)
        except Diary.DoesNotExist:
            return Response(
                {"message": "일기를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DiaryDetailSerializer(diary, context={"request": request})
        return Response(serializer.data)


class FriendCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_id, diary_id):
        result, code = create_friend_comment(
            request.user, friend_id, diary_id, request.data.get("content")
        )
        return Response(result, status=code)


class FriendCommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, friend_id, diary_id, comment_id):
        result, code = update_friend_comment(
            request.user, friend_id, diary_id, comment_id, request.data.get("content")
        )
        return Response(result, status=code)

    def delete(self, request, friend_id, diary_id, comment_id):
        result, code = delete_friend_comment(
            request.user, friend_id, diary_id, comment_id
        )
        return Response(result, status=code)


class FriendLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_id, diary_id):
        result, code = create_friend_diary_like(request.user, friend_id, diary_id)
        return Response(result, status=code)

    def delete(self, request, friend_id, diary_id):
        result, code = delete_friend_diary_like(request.user, friend_id, diary_id)
        return Response(result, status=code)


class FriendCommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, friend_id, diary_id, comment_id):
        result, code = create_friend_comment_like(
            request.user, friend_id, diary_id, comment_id
        )
        return Response(result, status=code)

    def delete(self, request, friend_id, diary_id, comment_id):
        result, code = delete_friend_comment_like(
            request.user, friend_id, diary_id, comment_id
        )
        return Response(result, status=code)
