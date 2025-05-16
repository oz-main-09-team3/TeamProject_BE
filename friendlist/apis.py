from django.db.models import Q

from friends.models import DiaryFriend
from users.models import User


def get_friends_by_status(user: User, status: str) -> list[User]:
    # 1) 나 → 상대 또는 상대 → 나 방향의 모든 DiaryFriend 레코드를 상태별로 필터
    queryset = DiaryFriend.objects.filter(
        Q(user=user, status=status) | Q(friend_user=user, status=status)
    )

    # 2) 각 관계에서 "나"가 아닌 쪽(User)만 골라냄
    friend_user_list: list[User] = []
    for relationship in queryset:
        if relationship.user_id == user.id:
            # relationship.user 는 항상 request.user 이므로,
            # friend_user 필드에 저장된 상대를 꺼낸다
            friend_user_list.append(relationship.friend_user)
        else:
            # 반대 방향으로 요청이 왔거나 받은 경우,
            # user 필드에 저장된 상대를 꺼낸다
            friend_user_list.append(relationship.user)

    return friend_user_list
