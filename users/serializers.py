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
        read_only_fields = ["id", "created_at"]


class OAuthLoginSerializer(serializers.Serializer):
    code = serializers.CharField()


class UserMeSerializer(serializers.ModelSerializer):
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
        read_only_fields = ["id", "username", "created_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname", "birthday", "profile", "phone_num"]
        extra_kwargs = {
            "nickname": {"required": False},
            "birthday": {"required": False},
            "profile": {"required": False},
            "phone_num": {"required": False},
        }
