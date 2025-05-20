from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from friends.models import DiaryFriend
from users.models import User

from .models import FriendList


@receiver(post_save, sender=DiaryFriend)
def sync_friendlist_on_save(sender, instance: DiaryFriend, created, **kwargs):
    user_a = instance.user
    user_b = User.objects.get(id=instance.friend_user_id.id)

    if instance.status == "accepted":
        # accepted 상태가 되면 양방향으로 FriendList 생성
        FriendList.objects.get_or_create(user=user_a, friend=user_b)
        FriendList.objects.get_or_create(user=user_b, friend=user_a)
    else:
        # pending/rejected 로 바뀌면 기존 레코드 삭제
        FriendList.objects.filter(user=user_a, friend=user_b).delete()
        FriendList.objects.filter(user=user_b, friend=user_a).delete()


@receiver(post_delete, sender=DiaryFriend)
def sync_friendlist_on_delete(sender, instance: DiaryFriend, **kwargs):
    user_a = instance.user
    user_b = User.objects.get(id=instance.friend_user_id.id)

    # 요청 자체가 삭제되면 FriendList도 삭제
    FriendList.objects.filter(user=user_a, friend=user_b).delete()
    FriendList.objects.filter(user=user_b, friend=user_a).delete()
