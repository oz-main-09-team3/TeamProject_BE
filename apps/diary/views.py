# views.py
from datetime import datetime

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .apis import (
    create_diary,
    delete_diary,
    get_calendar_diary_overview,
    get_diary_by_date,
    get_diary_detail,
    get_diary_list,
    update_diary,
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
    # TODO: 인증(user) 활성화 필요
    def post(self, request):
        # user = request.user (인증 구현 시)
        result = create_diary(None, request.data, request.FILES)
        return Response(result, status=status.HTTP_201_CREATED)

    def get(self, request, diary_id=None):
        # diary_id가 있으면 상세 조회
        # 없으면 목록 조회
        if diary_id:
            # 상세 조회
            try:
                diary = get_diary_detail(diary_id)
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
            diaries = get_diary_list(request)
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
        # user_id = request.user.id (인증 구현 시)
        now = datetime.now()
        year = int(request.query_params.get("year", now.year))
        month = int(request.query_params.get("month", now.month))

        calendar_data = get_calendar_diary_overview(None, year, month)
        serializer = CalendarDiarySerializer(calendar_data, many=True)
        return Response(serializer.data)


class DiaryByDateView(APIView):
    def get(self, request, date):
        # user_id = request.user.id (인증 구현 시)
        diaries = get_diary_by_date(None, date)

        if diaries is None:
            return Response(
                {
                    "message": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    def post(self, request, diary_id):
        try:
            diary = Diary.objects.get(id=diary_id)
            # [TODO] user=request.user 활성화 필요
            comment = Comment.objects.create(
                diary=diary,
                content=request.data.get("content"),
                # user=request.user
            )
            return Response({"comment_id": comment.id}, status=status.HTTP_201_CREATED)
        except Diary.DoesNotExist:
            return Response({"message": "일기를 찾을 수 없습니다"}, status=404)


class CommentDeleteView(APIView):
    def delete(self, request, diary_id, comment_id):
        try:
            # 1. 삭제 대상 댓글 조회 (is_deleted=False인 것만)
            comment = Comment.objects.get(
                id=comment_id, diary_id=diary_id, is_deleted=False
            )

            # 2. [TODO] 인증 구현 시 추가: request.user와 comment.user 일치 여부 확인
            # if comment.user != request.user:
            #     return Response(
            #         {"message": "권한이 없습니다"},
            #         status=status.HTTP_403_FORBIDDEN
            #     )

            # 3. 논리 삭제 처리
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
    def post(self, request, diary_id):
        try:
            diary = Diary.objects.get(id=diary_id)
            # [TODO] user=request.user 활성화 필요
            like, created = Like.objects.get_or_create(
                diary=diary,
                # user=request.user
            )
            return Response({"success": True}, status=status.HTTP_201_CREATED)
        except Diary.DoesNotExist:
            return Response({"message": "일기를 찾을 수 없습니다"}, status=404)


class LikeDeleteView(APIView):
    def delete(self, request, diary_id):
        try:
            # 1. 삭제 대상 좋아요 조회 (is_deleted=False인 것만)
            like = Like.objects.get(diary_id=diary_id, is_deleted=False)

            # 2. [TODO] 인증 구현 시 추가: request.user와 like.user 일치 여부 확인
            # if like.user != request.user:
            #     return Response(
            #         {"message": "권한이 없습니다"},
            #         status=status.HTTP_403_FORBIDDEN
            #     )

            # 3. 논리 삭제 처리
            like.is_deleted = True
            like.save()

            return Response({"success": True}, status=status.HTTP_200_OK)

        except Like.DoesNotExist:
            return Response(
                {"message": "존재하지 않는 좋아요입니다"},
                status=status.HTTP_404_NOT_FOUND,
            )


class EmotionListView(APIView):
    def get(self, request):
        emotions = Emotion.objects.all()
        serializer = EmotionSerializer(emotions, many=True)
        return Response(serializer.data)
