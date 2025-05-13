from django.db import models

from users.models import User


class FriendList(models.Model):
    user = models.ForeignKey(User, related_name="friends", on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name="friend_of", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "friend")

    def __str__(self):
        return f"{self.user.nickname} {self.friend.nickname}"
