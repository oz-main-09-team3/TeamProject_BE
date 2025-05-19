# apis.py

from django.utils import timezone

from users.models import User

from .models import DiaryFriend


def invite_friend(user, friend_user_id):
    # 이미 친구 요청이 있는지 확인
    if DiaryFriend.objects.filter(
        user=user, friend_user_id=friend_user_id, status="pending"
    ).exists():
        return None, "이미 요청한 친구입니다."
    try:
        friend_user = User.objects.get(id=friend_user_id)
    except User.DoesNotExist:
        return None, "존재하지 않는 유저입니다."
    diary_friend = DiaryFriend.objects.create(
        user=user, friend_user=friend_user, status="pending"
    )
    return diary_friend, None


def accept_friend_request(friend_id, current_user):
    try:
        diary_friend = DiaryFriend.objects.get(
            id=friend_id, friend_user_id=current_user
        )
    except DiaryFriend.DoesNotExist:
        return None, "요청이 없습니다."
    diary_friend.status = "accepted"
    diary_friend.responded_at = timezone.now()
    diary_friend.save()
    return diary_friend, None


def reject_friend_request(friend_id, current_user):
    try:
        diary_friend = DiaryFriend.objects.get(
            id=friend_id, friend_user_id=current_user
        )
    except DiaryFriend.DoesNotExist:
        return None, "요청이 없습니다."
    diary_friend.status = "rejected"
    diary_friend.responded_at = timezone.now()
    diary_friend.save()
    return diary_friend, None
