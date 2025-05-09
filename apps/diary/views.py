# views.py
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .apis import (
    create_diary,
    delete_diary,
    get_calendar_diary_overview,
    get_diary_by_date,
    get_diary_detail,
    get_diary_list,
    update_diary,
    create_comment_like,
    delete_comment_like,
    create_diary_like,
    delete_diary_like,
)
from .models import Comment, Diary, DiaryImage, Emotion, Like
from .serializers import (
    CalendarDiarySerializer,
    DiaryDetailSerializer,
    DiaryImageSerializer,
    DiarySerializer,
    EmotionSerializer,
)


class DiaryPagination(PageNumberPagination):
    page_size = 10


class DiaryView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        result = create_diary(request.user , request.data, request.FILES)
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request, diary_id=None):
        # diary_id가 있으면 상세 조회
        # 없으면 목록 조회
        if diary_id:
            # 상세 조회
            try:
                diary = Diary.objects.filter(id=diary_id, user=request.user, is_deleted=False).first()
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
            diaries = Diary.objects.filter(user=request.user, is_deleted=False)
            paginator = DiaryPagination()
            page = paginator.paginate_queryset(diaries, request)
            serializer = DiarySerializer(page, many=True)

            data = serializer.data
            for diary_data in data:
                diary = Diary.objects.get(id=diary_data["id"])
                diary_emotion = getattr(diary, "emotion", None)
                if diary_emotion:
                    diary_data["emotion"] = EmotionSerializer(
                        diary_emotion.emotion
                    ).data
                else:
                    diary_data["emotion"] = None

            return paginator.get_paginated_response(data)

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
            emotion_obj = Emotion.objects.filter(diary_id=diary_data["id"]).first()
            if emotion_obj:
                emotion_serializer = EmotionSerializer(emotion_obj)
                diary_data["emotion"] = emotion_serializer.data
            else:
                diary_data["emotion"] = None

        return Response(data)


class DiaryImageView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, diary_id):
        try:
            diary = Diary.objects.get(id=diary_id)
            image = request.FILES.get("image")
            # [TODO] S3 업로드 로직 추가
            diary_image = DiaryImage.objects.create(diary=diary, image_url=image.name)
            return Response({"diary_image_id": diary_image.id}, status=201)
        except Diary.DoesNotExist:
            return Response({"message": "일기를 찾을 수 없습니다"}, status=404)


class CommentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, diary_id):
        try:
            diary = Diary.objects.get(id=diary_id)
            comment = Comment.objects.create(
                diary=diary,
                content=request.data.get("content"),
                user=request.user
            )
            return Response({"comment_id": comment.id}, status=status.HTTP_201_CREATED)
        except Diary.DoesNotExist:
            return Response({"message": "일기를 찾을 수 없습니다"}, status=404)


class CommentDeleteView(APIView):
    def delete(self, request, diary_id, comment_id):
        permission_classes = [IsAuthenticated]
        try:
            comment = Comment.objects.get(
                id=comment_id, diary_id=diary_id, is_deleted=False
            )

            if comment.user != request.user:
                return Response(
                    {"message": "권한이 없습니다"},
                    status=status.HTTP_403_FORBIDDEN
                )

            comment.is_deleted = True
            comment.save()

            return Response({"success": True}, status=status.HTTP_200_OK)

        except Comment.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 댓글입니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CommentUpdateView(APIView):
    def patch(self, request, diary_id, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id, diary_id=diary_id)
            comment.content = request.data.get("content")
            comment.save()
            return Response({"success": True})
        except Comment.DoesNotExist:
            return Response({"message": "댓글 없음"}, status=404)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, diary_id):
        result, status_code = create_diary_like(diary_id, request.user)
        return Response(result, status=status_code)

class LikeDeleteView(APIView):
    permission_classes = [IsAuthenticated]
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