# views.py
from .models import Emotion

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime

from .apis import (
    create_diary,
    get_diary_detail,
    get_diary_list,
    update_diary,
    delete_diary,
    get_calendar_diary_overview,
    get_diary_by_date
)
from .serializers import (
    DiarySerializer,
    DiaryImageSerializer,
    EmotionSerializer,
    DiaryDetailSerializer,
    CalendarDiarySerializer
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
                    return Response({"error": "일기를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND)
                serializer = DiaryDetailSerializer(diary)
                return Response(serializer.data)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 목록 조회
            diaries = get_diary_list(request)
            paginator = DiaryPagination()
            page = paginator.paginate_queryset(diaries, request)
            serializer = DiarySerializer(page, many=True)

            data = serializer.data
            for diary_data in data:
                emotion_obj = Emotion.objects.filter(diary_id=diary_data['id']).first()
                if emotion_obj:
                    emotion_serializer = EmotionSerializer(emotion_obj)
                    diary_data['emotion'] = emotion_serializer.data
                else:
                    diary_data['emotion'] = None

            return paginator.get_paginated_response(data)

    def patch(self, request, diary_id):
        if not diary_id:
            return Response({"error": "일기 ID가 필요합니다"}, status=status.HTTP_400_BAD_REQUEST)

        result = update_diary(diary_id, request.data)
        if not result:
            return Response({"error": "일기를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"success": True})

    def delete(self, request, diary_id):
        if not diary_id:
            return Response({"error": "일기 ID가 필요합니다"}, status=status.HTTP_400_BAD_REQUEST)

        result = delete_diary(diary_id)
        if not result:
            return Response({"error": "일기를 찾을 수 없습니다"}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

class DiaryCalendarView(APIView):
    def get(self, request):
        # user_id = request.user.id (인증 구현 시)
        now = datetime.now()
        year = int(request.query_params.get('year', now.year))
        month = int(request.query_params.get('month', now.month))

        calendar_data = get_calendar_diary_overview(None, year, month)
        serializer = CalendarDiarySerializer(calendar_data, many=True)
        return Response(serializer.data)

class DiaryByDateView(APIView):
    def get(self, request, date):
        # user_id = request.user.id (인증 구현 시)
        diaries = get_diary_by_date(None, date)

        if diaries is None:
            return Response({"error": "날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식으로 입력해주세요."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = DiarySerializer(diaries, many=True)

        data = serializer.data
        for diary_data in data:
            emotion_obj = Emotion.objects.filter(diary_id=diary_data['id']).first()
            if emotion_obj:
                emotion_serializer = EmotionSerializer(emotion_obj)
                diary_data['emotion'] = emotion_serializer.data
            else:
                diary_data['emotion'] = None

        return Response(data)