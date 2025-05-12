from rest_framework import serializers

from friends.models import DiaryFriend


class DiaryFriendSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    friend_user_id = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DiaryFriend
        fields = [
            "id",
            "user",
            "friend_user_id",
            "status",
            "requested_at",
            "responded_at",
        ]


class FriendInviteRequestSerializer(serializers.ModelSerializer):
    friend_user_id = serializers.IntegerField()

    # def validate_
