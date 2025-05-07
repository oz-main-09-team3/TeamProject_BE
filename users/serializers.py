from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "birthday",
            "profile",
            "phone_num",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]


class OAuthLoginSerializer(serializers.Serializer):
    code = serializers.CharField()
