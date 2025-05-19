from django.db.models import Q

from friends.models import DiaryFriend
from users.models import User


def get_friends_by_status(user: User, status: str) -> list[User]:
    # 나 → 상대 또는 상대 → 나 방향의 모든 DiaryFriend 레코드를 상태별로 필터
    queryset = DiaryFriend.objects.filter(
        Q(user=user, status=status) | Q(friend_user=user, status=status)
    )

    friends: list[User] = []
    for rel in queryset:
        if rel.user == user:
            friends.append(rel.friend_user)
        else:
            friends.append(rel.user)
    return friends
