from collections import Counter
from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from emotion.models import Emotion, EmotionData
from emotion.serializers import EmotionSerializer, EmotionTrendViewSerializer
from emotion.utils import get_emotion_data_queryset

# # ReadOnlyModelViewSet : list(), retriev() 메소드만 자동 지원
# class EmotionViewSet(ReadOnlyModelViewSet):
#     queryset = Emotion.objects.all()  # Emotion 모델에 있는 모든 감정 데이터를 불러옴
#     serializer_class = EmotionSerializer  # EmotionSerializer를 사용해 JSON 형태로 변환
#     # /api/emotions/로 감정 리스트를 GET 요청하면 EmotionViewSet이 응답


# 감정 조회 전용 API
class EmotionListView(APIView):
    def get(self, request):
        emotions = Emotion.objects.all()
        data = [
            {
                "id": e.id,
                "emotion": e.emotion,
                "image_url": e.image_url,  # 이건 property 이므로 /static/emotions/1.png형태
            }
            for e in emotions
        ]
        return Response(data)


# 감정 변화 그래프
class EmotionTrendView(APIView):
    def get(self, request):
        queryset = get_emotion_data_queryset(request)
        if isinstance(
            queryset, Response
        ):  # queryset의 형태와 안맞으면 Response 클래스를 불러옴(에러 반환)
            return queryset
        response = EmotionTrendViewSerializer(queryset, many=True).data
        return Response(response)


# 감정 통계
class EmotionStatisticsView(APIView):
    def get(self, request):
        queryset = get_emotion_data_queryset(
            request
        )  # 사용자의 요청(request)을 기준으로 감정 데이터를 DB에서 가져옴
        if isinstance(
            queryset, Response
        ):  # queryset의 형태와 안맞으면 Response 클래스를 불러옴(에러 반환)
            return queryset
        counts = Counter([log.emotion for log in queryset])
        result = [
            {"emotion": EmotionSerializer(e).data, "count": count}
            for e, count in counts.items()
        ]
        return Response(result)


# class EmotionListView(APIView):
#     def get(self, request):
#         emotions = Emotion.objects.all()
#         serializer = EmotionSerializer(emotions, many=True)
#         return Response(serializer.data)
