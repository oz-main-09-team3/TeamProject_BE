# serializers.py
from rest_framework import serializers

from apps.diary.models import CommentLike, Diary, DiaryImage, Emotion
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "nickname", "profile"]


class DiarySerializer(serializers.ModelSerializer):
    emotion = serializers.SerializerMethodField()

    def get_emotion(self, obj):
        if hasattr(obj, "emotion") and obj.emotion:
            return EmotionSerializer(obj.emotion.emotion).data
        return None

    class Meta:
        model = Diary
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "updated_at",
            "visibility",
            "emotion",
        ]


class DiaryImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DiaryImage
        fields = ["id", "image_url"]

    def get_image_url(self, obj):
        return obj.image.url  # S3 URL 자동 생성


class DiaryDetailSerializer(serializers.ModelSerializer):
    images = DiaryImageSerializer(many=True, read_only=True)
    emotion = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = [
            "id",
            "user",
            "content",
            "visibility",
            "created_at",
            "updated_at",
            "images",
            "emotion",
            "comments",
            "like_count",
        ]

    def get_emotion(self, obj):
        diary_emotion = getattr(obj, "emotion", None)
        if diary_emotion:
            return EmotionSerializer(diary_emotion.emotion).data
        return None

    def get_like_count(self, obj):
        return obj.likes.filter(is_deleted=False).count()

    def get_comments(self, obj):
        comments = obj.comments.filter(is_deleted=False)
        result = []
        for c in comments:
            result.append(
                {
                    "comment_id": c.id,
                    "user": UserSerializer(c.user).data,  # user 정보 포함
                    "content": c.content,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "like_count": c.likes.filter(is_deleted=False).count(),
                }
            )
        return result


class CalendarDiarySerializer(serializers.Serializer):
    date = serializers.DateField()
    emotion_id = serializers.IntegerField(allow_null=True)
    emoji = serializers.CharField(allow_null=True)
    diary_id = serializers.IntegerField()


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ["id"]
