# views.py
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from emotion.serializers import EmotionSerializer

from .apis import (
    create_comment,
    create_comment_like,
    create_diary,
    create_diary_like,
    delete_comment,
    delete_comment_like,
    delete_diary,
    delete_diary_like,
    get_calendar_diary_overview,
    get_diary_by_date,
    get_diary_detail,
    get_diary_list,
    update_comment,
    update_diary,
)
from .models import Comment, Diary, DiaryEmotion, DiaryImage, Emotion, Like
from .serializers import (
    CalendarDiarySerializer,
    CommentSerializer,
    DiaryDetailSerializer,
    DiaryImageSerializer,
    DiarySerializer,
)


class DiaryPagination(PageNumberPagination):
    page_size = 10


class DiaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = create_diary(request.user, request.data, request.FILES)
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request, diary_id=None):
        # diary_id가 있으면 상세 조회
        # 없으면 목록 조회
        if diary_id:
            # 상세 조회
            try:
                diary = Diary.objects.filter(
                    id=diary_id, user=request.user, is_deleted=False
                ).first()
                if not diary:
                    return Response(
                        {"message": "일기를 찾을 수 없습니다"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                serializer = DiaryDetailSerializer(diary)
                return Response(serializer.data)
            except Exception as e:
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # 목록 조회
            diaries = Diary.objects.filter(
                user=request.user, is_deleted=False
            ).select_related("emotion__emotion")
            paginator = DiaryPagination()
            page = paginator.paginate_queryset(diaries, request)
            serializer = DiarySerializer(page, many=True)

            return paginator.get_paginated_response(serializer.data)

    def patch(self, request, diary_id):
        if not diary_id:
            return Response(
                {"message": "일기 ID가 필요합니다"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = update_diary(diary_id, request.data)
        if not result:
            return Response(
                {"message": "일기를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"success": True})

    def delete(self, request, diary_id):
        if not diary_id:
            return Response(
                {"message": "일기 ID가 필요합니다"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = delete_diary(diary_id)
        if not result:
            return Response(
                {"message": "일기를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)


class DiaryCalendarView(APIView):
    def get(self, request):
        now = datetime.now()
        year = int(request.query_params.get("year", now.year))
        month = int(request.query_params.get("month", now.month))

        calendar_data = get_calendar_diary_overview(request.user.id, year, month)
        serializer = CalendarDiarySerializer(calendar_data, many=True)
        return Response(serializer.data)


class DiaryByDateView(APIView):
    def get(self, request, date):
        diaries, error = get_diary_by_date(request.user, date)
        if error:
            return Response({"message": error}, status=400)

        serializer = DiarySerializer(diaries, many=True)
        data = serializer.data

        for diary_data in data:
            diary_emotion = DiaryEmotion.objects.filter(
                diary_id=diary_data["id"]
            ).first()
            if diary_emotion:
                diary_data["emotion"] = EmotionSerializer(diary_emotion.emotion).data
            else:
                diary_data["emotion"] = None

        return Response(data)


class DiaryImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, diary_id):
        try:
            diary = Diary.objects.get(id=diary_id)
            for img in request.FILES.getlist("images"):
                DiaryImage.objects.create(diary=diary, image=img)
            return Response({"success": True}, status=201)
        except Diary.DoesNotExist:
            return Response({"message": "일기를 찾을 수 없습니다"}, status=404)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diary_id):
        content = request.data.get("content")
        result, status_code = create_comment(request.user, diary_id, content)
        return Response(result, status=status_code)

    def get(self, request, diary_id):
        comments = Comment.objects.filter(diary_id=diary_id, is_deleted=False)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, diary_id, comment_id):
        result, status_code = delete_comment(request.user, diary_id, comment_id)
        return Response(result, status=status_code)


class CommentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, diary_id, comment_id):
        content = request.data.get("content")
        result, status_code = update_comment(
            request.user, diary_id, comment_id, content
        )
        return Response(result, status=status_code)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diary_id):
        result, status_code = create_diary_like(diary_id, request.user)
        return Response(result, status=status_code)

    def delete(self, request, diary_id):
        result, status_code = delete_diary_like(diary_id, request.user)
        return Response(result, status=status_code)


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, diary_id, comment_id):
        result, status_code = create_comment_like(diary_id, comment_id, request.user)
        return Response(result, status=status_code)

    def delete(self, request, diary_id, comment_id):
        permission_classes = [IsAuthenticated]
        result, status_code = delete_comment_like(diary_id, comment_id, request.user)
        return Response(result, status=status_code)
