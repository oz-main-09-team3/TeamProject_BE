# views.py
from datetime import datetime, timedelta

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
from .models import (
    Comment,
    Diary,
    DiaryEmotion,
    DiaryImage,
    Emotion,
    Like,
)
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

    @swagger_auto_schema(
        operation_description="일기 생성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="일기 내용"
                ),
                "visibility": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="공개 여부 (기본값: False)"
                ),
                "emotion_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="감정 ID"
                ),
            },
            example={
                "content": "오늘은 행복한 하루!",
                "visibility": True,
                "emotion_id": 1,
            },
        ),
        responses={
            201: openapi.Response(
                description="성공 응답",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"diary_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
                    example={"diary_id": 123},
                ),
            ),
            400: "잘못된 요청",
        },
    )
    def post(self, request):
        result = create_diary(request.user, request.data, request.FILES)
        return Response(result, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="일기 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                "emotion",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="감정 타입 필터링",
            ),
            openapi.Parameter(
                "date_from",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="YYYY-MM-DD",
            ),
            openapi.Parameter(
                "date_to",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="YYYY-MM-DD",
            ),
        ],
        responses={
            200: openapi.Response(
                description="성공 응답",
                schema=DiarySerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user": {"id": 1, "username": "user1"},
                            "content": "첫 번째 일기",
                            "visibility": True,
                            "emotion": {"id": 1, "emoji": "😊"},
                        }
                    ]
                },
            )
        },
    )
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

    @swagger_auto_schema(
        operation_description="일기 수정",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "content": openapi.Schema(type=openapi.TYPE_STRING),
                "visibility": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                "emotion_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            example={"content": "수정된 내용"},
        ),
        responses={
            200: openapi.Response(
                description="수정 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            404: "존재하지 않는 일기",
        },
    )
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

    @swagger_auto_schema(
        operation_description="일기 삭제",
        responses={
            204: openapi.Response(description="삭제 성공"),
            404: openapi.Response(
                description="존재하지 않는 일기",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "일기를 찾을 수 없습니다"},
                ),
            ),
        },
    )
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
    @swagger_auto_schema(
        operation_description="달력형 일기 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                "year", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                "month", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="성공 응답",
                schema=CalendarDiarySerializer(many=True),
                examples={
                    "application/json": [
                        {
                            "date": "2025-07-01",
                            "emotion_id": 1,
                            "emoji": "😊",
                            "diary_id": 123,
                        }
                    ]
                },
            )
        },
    )
    def get(self, request):
        now = datetime.now()
        year = int(request.query_params.get("year", now.year))
        month = int(request.query_params.get("month", now.month))

        calendar_data = get_calendar_diary_overview(request.user.id, year, month)
        serializer = CalendarDiarySerializer(calendar_data, many=True)
        return Response(serializer.data)


class DiaryByDateView(APIView):
    @swagger_auto_schema(
        operation_description="특정 날짜 일기 조회",
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="YYYY-MM-DD",
                required=True,
            )
        ],
        responses={
            200: DiarySerializer(many=True),
            400: openapi.Response(
                description="잘못된 날짜 형식",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "날짜 형식 오류"},
                ),
            ),
        },
    )
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

    @swagger_auto_schema(
        operation_description="이미지 업로드",
        manual_parameters=[
            openapi.Parameter(
                "image", openapi.IN_FORM, type=openapi.TYPE_FILE, required=True
            )
        ],
        responses={
            201: openapi.Response(
                description="업로드 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "diary_image_id": openapi.Schema(type=openapi.TYPE_INTEGER)
                    },
                    example={"diary_image_id": 456},
                ),
            ),
            404: openapi.Response(
                description="존재하지 않는 일기",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "일기를 찾을 수 없습니다"},
                ),
            ),
        },
    )
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

    @swagger_auto_schema(
        operation_description="댓글 작성",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["content"],
            properties={"content": openapi.Schema(type=openapi.TYPE_STRING)},
            example={"content": "댓글 내용"},
        ),
        responses={
            201: openapi.Response(
                description="생성 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "comment_id": openapi.Schema(type=openapi.TYPE_INTEGER)
                    },
                    example={"comment_id": 456},
                ),
            ),
            404: "존재하지 않는 일기",
        },
    )
    def post(self, request, diary_id):
        content = request.data.get("content")
        result, status_code = create_comment(request.user, diary_id, content)
        return Response(result, status=status_code)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="댓글 삭제",
        responses={
            200: openapi.Response(
                description="삭제 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            403: openapi.Response(
                description="권한 없음",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "권한이 없습니다"},
                ),
            ),
            404: openapi.Response(
                description="존재하지 않는 댓글",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "존재하지 않는 댓글입니다"},
                ),
            ),
        },
    )
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

    @swagger_auto_schema(
        operation_description="좋아요 추가",
        responses={
            201: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            404: "존재하지 않는 일기",
        },
    )
    def post(self, request, diary_id):
        result, status_code = create_diary_like(diary_id, request.user)
        return Response(result, status=status_code)

    @swagger_auto_schema(
        operation_description="좋아요 취소",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            404: openapi.Response(
                description="존재하지 않는 좋아요",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"message": "존재하지 않는 좋아요입니다"},
                ),
            ),
        },
    )
    def delete(self, request, diary_id):
        result, status_code = delete_diary_like(diary_id, request.user)
        return Response(result, status=status_code)


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="댓글 좋아요 추가",
        responses={
            201: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            400: "이미 좋아요를 누름",
            404: "존재하지 않는 댓글",
        },
    )
    def post(self, request, diary_id, comment_id):
        result, status_code = create_comment_like(diary_id, comment_id, request.user)
        return Response(result, status=status_code)

    @swagger_auto_schema(
        operation_description="댓글 좋아요 취소",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"success": openapi.Schema(type=openapi.TYPE_BOOLEAN)},
                    example={"success": True},
                ),
            ),
            404: openapi.Response(
                description="존재하지 않는 좋아요",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                    example={"error": "존재하지 않는 댓글 또는 좋아요입니다"},
                ),
            ),
        },
    )
    def delete(self, request, diary_id, comment_id):
        permission_classes = [IsAuthenticated]
        result, status_code = delete_comment_like(diary_id, comment_id, request.user)
        return Response(result, status=status_code)
