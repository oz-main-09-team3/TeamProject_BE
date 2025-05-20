from django.db.models import Q

from friends.models import DiaryFriend
from users.models import User


def get_friends_by_status(user, status):
    return User.objects.filter(
        Q(
            receive_friend__user=user, receive_friend__status=status
        )  # 내가 받은 요청 중 status에 해당하는 요청의 보낸 사람
        | Q(
            send_friend__friend_user=user, send_friend__status=status
        )  # 내가 보낸 요청 중 status에 해당하는 요청의 받은 사람
    ).distinct()
