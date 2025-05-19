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
    _check_friend_or_403(user, friend_id)
    return diary_get_calendar(friend_id, year, month)


def get_friend_diaries_by_date(user, friend_id, date_str):
    _check_friend_or_403(user, friend_id)
    # diary_get_by_date는 (queryset, error_msg) 튜플 반환
    return diary_get_by_date(friend_id, date_str)


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
