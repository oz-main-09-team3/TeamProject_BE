from rest_framework import serializers
from users.models import User


class FriendListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nickname", "profile"]