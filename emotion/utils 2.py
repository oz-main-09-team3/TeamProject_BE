from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from rest_framework.response import Response

from emotion.models import EmotionData


# 문자열로 들어온 날짜 (from, to)를 실제 날짜 객체로 바꿔주고, 그걸 Django에서 사용할 수 있는 시간대-aware datatime으로 바꿔줌
# 만약 잘못 입력 했으면 400 Bad Request 에러를 반환
def get_date_range_or_response(from_str, to_str):
    if (
        not from_str or not to_str
    ):  # 사용자가 ?from=...&to=... 이런 식으로 날짜를 주지 않았거나 둘중에 하나라도 빠졌으면
        return Response(
            {"detail": "날짜 쿼리 파라미터가 필요합니다."}, status=400
        )  # 400에러 반환
    try:  # 예) "2025-05-09" -> datetime(2025, 5, 9), make_aware()는 타임존을 포함시켜 줌(Django는 시간대가 포함된 datetime을 선호)
        start_dt = make_aware(datetime.strptime(from_str, "%Y-%m-%d"))
        # to 날짜에는 +1를 더함: 예) "2025-05-09 -> 2025-05-10 00:00까지 포함되도록, 이렇게 하면 created_at__lt=end_dt 조건으로 "2025-05-9 전체"를 포함할 수 있음
        end_dt = make_aware(datetime.strptime(to_str, "%Y-%m-%d") + timedelta(days=1))
    except (
        ValueError
    ):  # 날짜 형식이 이상한 경우 에러를 발생해 사용자에게 날짜 형식이 잘 못 되었다고 알려줌, 400 에러 반환
        return Response({"detail": "날짜 형식은 YYYY-MM-DD여야 합니다."}, status=400)
    return start_dt, end_dt  # 정상적인 경우 두개의 datetime 객체를 튜플로 돌려줌


# 사용자의 HTTP 요청(request)에서 날짜 범위를 꺼내서 EmotionData모델에서 그 범위에 해당하는 감정 데이터를 찾아주는 함수
def get_emotion_data_queryset(request):
    # URL에서 ?from=YYYY-MM-DD&to=YYYY-MM-DD 형태로 들어온 값을 꺼내고 그걸 위에서 만든 get_date_range_or_response 함수에 넘김
    result = get_date_range_or_response(
        request.query_params.get("from"), request.query_params.get("to")
    )
    # isinstance: 이 객체(여기선 result)가 해당 클래스의 인스턴스인지 확인하는 함수
    # 만약 날짜 형식이 잘못되었거나 둘중 하나라도 없으면 from rest_framework.response import Response의 Response를 불러옴
    if isinstance(result, Response):
        return result
    start_dt, end_dt = result  # 정상적인 경우는 날짜 튜플이 반환
    # 감정 데이터를 created_at 필드 기준으로 필터
    return EmotionData.objects.filter(created_at__gte=start_dt, created_at__lt=end_dt)
