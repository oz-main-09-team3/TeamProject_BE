# apis.py
from .models import Diary, DiaryImage, Emotion
from datetime import datetime
from collections import defaultdict

def create_diary(user, data, files):
    """
    TODO:
    - 인증(user) 활성화 (user 파라미터 적용)
    - 이미지 파일 S3 업로드 연동 (image_url → S3 URL)
    - 좋아요/댓글 기능 연동 (Diary 모델 확장 필요)
    """
    # Diary 생성
    content = data.get('content')
    visibility = data.get('visibility', False)
    diary = Diary.objects.create(
        # user=user, # 나중에 활성화
        content=content,
        visibility=visibility,
    )

    # 이미지 저장
    images = files.getlist('images') if hasattr(files, 'getlist') else []

    for img in images:
        DiaryImage.objects.create(
            diary=diary,
            image_url=img.name,  # 나중에 s3 url로 바꾸기
        )

    # 감정 저장
    emoji = data.get('emoji')
    emotion = data.get('emotion')
    if emoji and emotion:
        Emotion.objects.create(
            diary=diary,
            emoji=emoji,
            emotion=emotion,
        )

    return {'diary_id': diary.id}

# 일기 목록 조회
def get_diary_list(request):
    # 필터링 파라미터
    user_id = request.query_params.get('user_id')
    emotion_type = request.query_params.get('emotion')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    visibility = request.query_params.get('visibility')
    search_keyword = request.query_params.get('keyword')

    # 기본 쿼리셋
    diaries = Diary.objects.all()

    # 필터 적용
    if user_id:
        diaries = diaries.filter(user_id=user_id)

    if emotion_type:
        diary_ids = Emotion.objects.filter(emotion=emotion_type).values_list('diary_id', flat=True)
        diaries = diaries.filter(id__in=diary_ids)

    if date_from and date_to:
        diaries = diaries.filter(created_at__range=[date_from, date_to])

    if visibility is not None:
        diaries = diaries.filter(visibility=visibility)

    if search_keyword:
        diaries = diaries.filter(content__icontains=search_keyword)

    # 최신순 정렬
    diaries = diaries.order_by('-created_at')

    return diaries

# 달력형 일기 목록(날짜별 대표 감정 이모지) 조회"
def get_calendar_diary_overview(user_id, year, month):
    # 1. 해당 월의 모든 일기 조회
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    diaries = Diary.objects.filter(
        # user_id=user_id, # 나중에 활성화
        created_at__gte=start_date,
        created_at__lt=end_date
    ).order_by('created_at')

    # 2. 날짜별로 그룹핑 (YYYY-MM-DD)
    diary_by_date = defaultdict(list)
    for diary in diaries:
        date_str = diary.created_at.strftime('%Y-%m-%d')
        diary_by_date[date_str].append(diary)

    # 3. 날짜별 대표 일기(마지막 작성 일기)만 추출
    calendar_data = []
    for date_str, diary_list in diary_by_date.items():
        diary = diary_list[-1]  # 마지막 일기
        emotion = Emotion.objects.filter(diary=diary).first()
        calendar_data.append({
            'date': date_str,
            'emotion': emotion.emotion if emotion else None,
            'emoji': emotion.emoji if emotion else None,
            'diary_id': diary.id
        })

    return calendar_data

# API 응답 예시
# [
#   {"date": "2025-07-01", "emotion": "happy", "emoji": "url", "diary_id": 123},
#   {"date": "2025-07-02", "emotion": "sad", "emoji": "url", "diary_id": 124},
#   ...
# ]


# 특정 날짜의 일기 목록 조회
def get_diary_by_date(user_id, date):
    try:
        # date는 'YYYY-MM-DD' 형식
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        next_day = datetime(date_obj.year, date_obj.month, date_obj.day + 1) if date_obj.day < 28 else datetime(
            date_obj.year, date_obj.month + 1, 1)

        diaries = Diary.objects.filter(
            # user_id=user_id,  # 나중에 활성화
            created_at__gte=date_obj,
            created_at__lt=next_day
        ).order_by('-created_at')

        return diaries
    except ValueError:
        # 날짜 형식이 잘못된 경우
        return None

# 일기 상세 조회
def get_diary_detail(diary_id):
    """
    TODO:
    - 좋아요/댓글 정보 추가 (Like, Comment 모델 연동)
    """
    ...
    try:
        diary = Diary.objects.get(id=diary_id)
    except Diary.DoesNotExist:
        return None
    images = list(DiaryImage.objects.filter(diary=diary).values('image_url'))
    emotion = Emotion.objects.filter(diary=diary).first()
    return {
        'diary_id': diary.id,
        'content': diary.content,
        'created_at': diary.created_at,
        'updated_at': diary.updated_at,
        'visibility': diary.visibility,
        'images': images,
        'emotion': {
            'emoji': emotion.emoji if emotion else None,
            'emotion': emotion.emotion if emotion else None,
        }
    }

def update_diary(diary_id, data):
    try:
        diary = Diary.objects.get(id=diary_id)
    except Diary.DoesNotExist:
        return False
    content = data.get('content')
    visibility = data.get('visibility')
    if content:
        diary.content = content
    if visibility is not None:
        diary.visibility = visibility
    diary.save()
    return True

def delete_diary(diary_id):
    try:
        diary = Diary.objects.get(id=diary_id)
    except Diary.DoesNotExist:
        return False
    diary.delete()
    return True