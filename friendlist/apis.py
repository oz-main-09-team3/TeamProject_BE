from rest_framework.exceptions import NotFound
from users.models import User
from friendlist.models import FriendList


def get_friend_list(user):
    friend_relations = FriendList.objects.filter(user=user)
    friends = [relation.friend for relation in friend_relations]
    return friends


def delete_friend(user, friend_id):
    try:
        friend_relation = FriendList.objects.get(user=user, friend_id=friend_id)
        friend_relation.delete()
    except FriendList.DoesNotExist:
        raise NotFound("친구를 찾을 수 없습니다")