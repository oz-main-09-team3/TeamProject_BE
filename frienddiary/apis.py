from django.db.models import Q
from rest_framework.exceptions import PermissionDenied

from apps.diary.apis import create_comment as orig_create_comment
from apps.diary.apis import create_comment_like as orig_create_comment_like
from apps.diary.apis import create_diary_like as orig_create_diary_like
from apps.diary.apis import delete_comment as orig_delete_comment
from apps.diary.apis import delete_comment_like as orig_delete_comment_like
from apps.diary.apis import delete_diary_like as orig_delete_diary_like
from apps.diary.apis import get_calendar_diary_overview as diary_get_calendar
from apps.diary.apis import get_diary_by_date as diary_get_by_date
from apps.diary.apis import update_comment as orig_update_comment
from apps.diary.models import Diary
from friends.models import DiaryFriend


def _check_friend_or_403(user, friend_id: int):
    """
    user ↔ friend_id 가 DiaryFriend에 accepted 상태로 존재하는지 검사.
    """
    if not DiaryFriend.objects.filter(
        Q(user=user, friend_user_id=friend_id)
        | Q(user_id=friend_id, friend_user_id=user),
        status="accepted",
    ).exists():
        raise PermissionDenied("친구 관계가 아닙니다.")


def get_friend_calendar_overview(user, friend_id, year, month):
    # 1) 권한 체크
    _check_friend_or_403(user, friend_id)

    # 2) 기존 달력용 데이터 가져오기 (date, emotion_id, emoji, diary_id)
    raw = diary_get_calendar(friend_id, year, month)

    # 3) diary_id로 Diary 객체를 조회해 content를 추가
    for day in raw:
        diary_id = day.get("diary_id")
        if diary_id is None:
            day["content"] = None
            continue

        try:
            # is_deleted 필드가 있을 경우 필터에 추가
            diary = Diary.objects.get(id=diary_id, is_deleted=False)
            day["content"] = diary.content
        except Diary.DoesNotExist:
            day["content"] = None

    # 4) 수정된 리스트 반환
    return raw


def get_friend_diaries_over_month(user, friend_id, year=None, month=None):
    """
    현재 연·월(또는 전체) 일기 리스트를 반환합니다.
    """
    if not _check_friend_or_403(user, friend_id):
        raise PermissionDenied("친구 관계가 아닙니다.")

    qs = Diary.objects.filter(user_id=friend_id, is_deleted=False)
    if year:
        qs = qs.filter(created_at__year=year)
    if month:
        qs = qs.filter(created_at__month=month)

    return qs.order_by("-created_at")


def create_friend_comment(user, friend_id, diary_id, content):
    _check_friend_or_403(user, friend_id)
    return orig_create_comment(user, diary_id, content)


def update_friend_comment(user, friend_id, diary_id, comment_id, content):
    _check_friend_or_403(user, friend_id)
    return orig_update_comment(user, diary_id, comment_id, content)


def delete_friend_comment(user, friend_id, diary_id, comment_id):
    _check_friend_or_403(user, friend_id)
    return orig_delete_comment(user, diary_id, comment_id)


def create_friend_diary_like(user, friend_id, diary_id):
    _check_friend_or_403(user, friend_id)
    return orig_create_diary_like(diary_id, user)


def delete_friend_diary_like(user, friend_id, diary_id):
    _check_friend_or_403(user, friend_id)
    return orig_delete_diary_like(diary_id, user)


def create_friend_comment_like(user, friend_id, diary_id, comment_id):
    _check_friend_or_403(user, friend_id)
    return orig_create_comment_like(diary_id, comment_id, user)


def delete_friend_comment_like(user, friend_id, diary_id, comment_id):
    _check_friend_or_403(user, friend_id)
    return orig_delete_comment_like(diary_id, comment_id, user)
