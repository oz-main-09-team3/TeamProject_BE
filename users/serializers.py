from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # ImageField 에 업로드된 S3 URL 을 반환합니다
    profile = serializers.ImageField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "birthday",
            "email",
            "phone_num",
            "profile",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OAuthLoginSerializer(serializers.Serializer):
    code = serializers.CharField()


class UserMeSerializer(serializers.ModelSerializer):
    profile = serializers.ImageField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "nickname",
            "birthday",
            "email",
            "phone_num",
            "profile",
            "created_at",
        ]
        read_only_fields = ["id", "username", "created_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField(
        required=False,
        allow_null=True,  # null 허용
    )

    class Meta:
        model = User
        fields = ["nickname", "birthday", "profile", "phone_num", "email"]
        extra_kwargs = {
            "nickname": {"required": False},
            "birthday": {"required": False},
            "profile": {"required": False},
            "phone_num": {"required": False},
            "email": {"required": False},
        }
