# apis.py
from collections import defaultdict
from datetime import datetime, timedelta

from django.utils import timezone

from .models import Diary, DiaryEmotion, DiaryImage, Emotion, Comment, CommentLike, Like


def create_diary(user, data, files):
    content = data.get("content")
    visibility = data.get("visibility", False)
    diary = Diary.objects.create(
        user=user,
        content=content,
        visibility=visibility,
    )

    images = files.getlist("images") if hasattr(files, "getlist") else []
    for img in images:
        DiaryImage.objects.create(
            diary=diary,
            image_url=img.name,  # 추후 S3 URL로 변경
        )

    emotion_id = data.get("emotion_id")
    if emotion_id:
        emotion = Emotion.objects.filter(id=emotion_id).first()
        if emotion:
            DiaryEmotion.objects.create(diary=diary, emotion=emotion)

    return {"diary_id": diary.id}


# 일기 목록 조회
def get_diary_list(request):
    # 필터링 파라미터
    user_id = request.query_params.get("user_id")
    emotion_type = request.query_params.get("emotion")
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    visibility = request.query_params.get("visibility")
    search_keyword = request.query_params.get("keyword")

    # 기본 쿼리셋
    diaries = Diary.objects.filter(is_deleted=False)

    # 필터 적용
    if user_id:
        diaries = diaries.filter(user_id=user_id)

    if emotion_type:
        diary_ids = DiaryEmotion.objects.filter(
            emotion__emotion=emotion_type
        ).values_list("diary_id", flat=True)
        diaries = diaries.filter(id__in=diary_ids)

    if date_from and date_to:
        diaries = diaries.filter(created_at__range=[date_from, date_to])

    if visibility is not None:
        diaries = diaries.filter(visibility=visibility)

    if search_keyword:
        diaries = diaries.filter(content__icontains=search_keyword)

    # 최신순 정렬
    diaries = diaries.order_by("-created_at")

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
        created_at__lt=end_date,
    ).order_by("created_at")

    # 2. 날짜별로 그룹핑 (YYYY-MM-DD)
    diary_by_date = defaultdict(list)
    for diary in diaries:
        date_str = diary.created_at.strftime("%Y-%m-%d")
        diary_by_date[date_str].append(diary)

    # 3. 날짜별 대표 일기(마지막 작성 일기)만 추출
    calendar_data = []
    for date_str, diary_list in diary_by_date.items():
        diary = diary_list[-1]  # 마지막 일기

        diary_emotion = getattr(diary, "emotion", None)
        if diary_emotion:
            emotion = diary_emotion.emotion
        else:
            emotion = None

        calendar_data.append(
            {
                "date": date_str,
                "emotion_id": emotion.id if emotion else None,
                "emoji": emotion.emoji if emotion else None,
                "diary_id": diary.id,
            }
        )

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
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        next_day = date_obj + timedelta(days=1)

        diaries = Diary.objects.filter(
            # user_id=user_id,  # 나중에 활성화
            created_at__gte=date_obj,
            created_at__lt=next_day,
        ).order_by("-created_at")

        return diaries
    except ValueError:
        # 날짜 형식이 잘못된 경우
        return None


# 일기 상세 조회
def get_diary_detail(diary_id):
    try:
        diary = Diary.objects.get(id=diary_id, is_deleted=False)
    except Diary.DoesNotExist:
        return None

    images = list(diary.images.filter(is_deleted=False).values("image_url"))
    diary_emotion = getattr(diary, "emotion", None)
    emotion_data = None
    if diary_emotion:
        emotion_data = {
            "emoji": diary_emotion.emotion.emoji,
            "emotion": diary_emotion.emotion.emotion,
        }

    comments = diary.comments.filter(is_deleted=False).values(
        "id", "user_id", "content", "created_at", "updated_at"
    )
    like_count = diary.likes.filter(is_deleted=False).count()

    return {
        "diary_id": diary.id,
        "user": {
            "user_id": diary.user.id,
            "username": diary.user.username,
            "nickname": getattr(diary.user, "nickname", ""),
            "profile_image": getattr(diary.user, "profile_image", ""),
        },
        "content": diary.content,
        "visibility": diary.visibility,
        "created_at": diary.created_at,
        "updated_at": diary.updated_at,
        "images": images,
        "emotion": emotion_data,
        "comments": list(comments),
        "like_count": like_count,
    }


def update_diary(diary_id, data):
    try:
        diary = Diary.objects.get(id=diary_id)
    except Diary.DoesNotExist:
        return False

    emotion_id = data.get("emotion_id")
    if emotion_id:
        emotion = Emotion.objects.filter(id=emotion_id).first()
        if emotion:
            # 기존 감정 삭제 후 새로 연결
            DiaryEmotion.objects.filter(diary=diary).delete()
            DiaryEmotion.objects.create(diary=diary, emotion=emotion)

    content = data.get("content")
    visibility = data.get("visibility")

    if content:
        diary.content = content

    if visibility is not None:
        diary.visibility = visibility

    diary.updated_at = timezone.now()
    diary.save()
    return True


def delete_diary(diary_id):
    try:
        diary = Diary.objects.get(id=diary_id)
    except Diary.DoesNotExist:
        return False
    diary.is_deleted = True
    diary.save()
    return True


def create_diary_like(diary_id):
    try:
        diary = Diary.objects.get(id=diary_id)
        # user = request.user  # user 구현 시 활성화
        like, created = Like.objects.get_or_create(
            diary=diary,
            # user=user
        )
        return {"success": True}, 201
    except Diary.DoesNotExist:
        return {"message": "일기를 찾을 수 없습니다"}, 404

def delete_diary_like(diary_id):
    try:
        like = Like.objects.get(diary_id=diary_id, is_deleted=False)
        # user = request.user  # user 구현 시 활성화
        # if like.user != request.user:
        #     return {"message": "권한이 없습니다"}, 403
        like.is_deleted = True
        like.save()
        return {"success": True}, 200
    except Like.DoesNotExist:
        return {"message": "존재하지 않는 좋아요입니다"}, 404


def create_comment_like(diary_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, diary_id=diary_id, is_deleted=False)
        # user = request.user  # user 구현 시 활성화
        like, created = CommentLike.objects.get_or_create(
            comment=comment,
            # user=user,
            is_deleted=False
        )
        if not created:
            return {"error": "이미 좋아요를 눌렀습니다."}, 400
        return {"success": True}, 201
    except Comment.DoesNotExist:
        return {"error": "존재하지 않는 댓글입니다."}, 404


def delete_comment_like(diary_id, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, diary_id=diary_id, is_deleted=False)
        # user = request.user  # user 구현 시 활성화
        like = CommentLike.objects.get(
            comment=comment,
            # user=user,
            is_deleted=False
        )
        like.is_deleted = True
        like.save()
        return {"success": True}, 200
    except (Comment.DoesNotExist, CommentLike.DoesNotExist):
        return {"error": "존재하지 않는 댓글 또는 좋아요입니다."}, 404