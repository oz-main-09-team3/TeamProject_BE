from django.db.models import Q

from friends.models import DiaryFriend
from users.models import User


def get_friends_by_status(user, status):
    return User.objects.filter(
        Q(diaryfriend__user=user, diaryfriend__status=status)
        | Q(diaryfriend__friend_user=user, diaryfriend__status=status)
    ).distinct()
