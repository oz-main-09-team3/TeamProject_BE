from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.diary.models import (
    Diary,
    DiaryEmotion,
)
from apps.diary.serializers import (
    CalendarDiarySerializer,
    DiaryDetailSerializer,
    DiarySerializer,
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
    get_friend_diaries_by_date,
    update_friend_comment,
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


class FriendDiaryByDateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, friend_id, date):
        if not _check_friend_or_terminate(request.user, friend_id):
            return Response(
                {"message": "친구 관계가 아닙니다."}, status=status.HTTP_403_FORBIDDEN
            )

        diaries, error = get_friend_diaries_by_date(request.user, friend_id, date)
        if error:
            return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DiarySerializer(diaries, many=True, context={"request": request})
        data = serializer.data

        # 기존 DiaryByDateView 방식대로 emotion 채우기
        for d in data:
            emo = DiaryEmotion.objects.filter(diary_id=d["id"]).first()
            d["emotion"] = EmotionSerializer(emo.emotion).data if emo else None

        return Response(data)


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
