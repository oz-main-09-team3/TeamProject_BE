from collections import Counter
from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from emotion.models import Emotion, EmotionData
from emotion.serializers import EmotionSerializer, EmotionTrendViewSerializer


# 감정 조회 전용 API
# ReadOnlyModelViewSet : list(), retriev() 메소드만 자동 지원
class EmotionViewSet(ReadOnlyModelViewSet):
    queryset = Emotion.objects.all()  # Emotion 모델에 있는 모든 감정 데이터를 불러옴
    serializer_class = EmotionSerializer  # EmotionSerializer를 사용해 JSON 형태로 변환
    # /api/emotions/로 감정 리스트를 GET 요청하면 EmotionViewSet이 응답


class EmotionTrendView(APIView):
    def get(self, request):
        start = request.query_params.get(
            "from"
        )  # query_params.get(): URL의 쿼리 파라미터 ?from=...&to=...를 가져옴
        end = request.query_params.get("to")
        # 날짜가 안 들어왔을 경우 400 Bad Request 상태 에러 반환
        if not start or not end:
            return Response({"detail": "날짜 쿼리 파라미터가 필요합니다."}, status=400)
        # 날짜 형식이 잘못됐을 경우 예외 처리.
        # 날짜 문자열 (YYYY-MM-DD)을 datetime으로 변환
        # make_aware: Django가 timezone-aware datetime 객체를 요구하기 때문에 사용
        # 종료일에 +1일을 더하는 이유는 "해당 날짜까지 포함"되게 하기 위함
        try:
            start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
            end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))
        except ValueError:  # 날짜 쿼리의 형식이 안맞으면 400 에러 반환
            return Response(
                {"detail": "날짜 형식은 YYYY-MM-DD여야 합니다."}, status=400
            )

        # 위 조건이 맞을 경우 EmotionData 모델에서 해당 날짜 범위의 데이터만 필터링
        data = EmotionData.objects.filter(
            created_at__gte=start_dt, created_at__lt=end_dt
        )
        response = EmotionTrendViewSerializer(
            data, many=True
        ).data  # EmotionTrendViewSerializer로 JSON 형태로 직렬화
        return Response(response)  # 직렬화한 데이터 반환


# 감정 사용 로그를 특정 기간 동안 집계하기 위한 API
# 이 API는 차트에서 감정별 빈도를 나타내야 할 때 사용
class EmotionCountView(APIView):
    def get(self, request):
        start = request.query_params.get(
            "from"
        )  # query_params.get(): URL의 쿼리 파라미터 ?from=...&to=...를 가져옴
        end = request.query_params.get("to")
        # 날짜가 안 들어왔을 경우 400 Bad Request 에러 반환
        if not start or not end:
            return Response({"detail": "날짜 쿼리 파라미터가 필요합니다."}, status=400)
        # 날짜 형식이 잘못됐을 경우 예외 처리.
        # 날짜 문자열 (YYYY-MM-DD)을 datetime으로 변환
        # make_aware: Django가 timezone-aware datetime 객체를 요구하기 때문에 사용
        # 종료일에 +1일을 더하는 이유는 "해당 날짜까지 포함"되게 하기 위함
        try:
            start_dt = make_aware(datetime.strptime(start, "%Y-%m-%d"))
            end_dt = make_aware(datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1))
        except ValueError:  # 날짜 쿼리의 형식이 안맞으면 400 에러 반환
            return Response(
                {"detail": "날짜 형식은 YYYY-MM-DD여야 합니다."}, status=400
            )

        # 특정 날짜 사이에 기록된 감정 필터링 후 해당 감정의 사용된 횟수 세기
        # EmotionData 테이블에서 날짜가 start_dt 이상이고, end_dt 미만인 데이터 가져옴(해당 날짜 범위 안에 기록된 감정 로그들)
        logs = EmotionData.objects.filter(
            created_at__gte=start_dt, created_at__lt=end_dt
        )
        # Counter: 감정별 사용 횟수 세기
        # 불러온 로그들에서 log.emtion을 리스트로 모으고, Counter로 감정별 사용 횟수를 센다
        counts = Counter([log.emotion for log in logs])
        # Counter로 센 감정 객체 e를 EmotionSerializer로 감싸 JSON 형태로 만들고, 사용횟수 count와 함께 딕셔너리로 묶음
        result = [
            {"emotion": EmotionSerializer(e).data, "count": count}
            for e, count in counts.items()
        ]
        return Response(result)
