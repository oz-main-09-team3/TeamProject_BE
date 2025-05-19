from rest_framework import serializers

from apps.diary.models import CommentLike, Diary, Like
from apps.diary.serializers import UserSerializer
from emotion.serializers import EmotionSerializer


class CalendarDiarySerializer(serializers.Serializer):
    date = serializers.DateField()
    emotion_id = serializers.IntegerField(allow_null=True)
    emoji = serializers.CharField(allow_null=True)
    diary_id = serializers.IntegerField()
    content = serializers.CharField(allow_null=True)


class DiaryListSerializer(serializers.ModelSerializer):
    emotion = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

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

    def get_emotion(self, obj):
        diary_emotion = getattr(obj, "emotion", None)
        if diary_emotion:
            return EmotionSerializer(diary_emotion.emotion).data
        return None

    def get_like_count(self, obj):
        # apps.diary.models.Like.related_name="likes"
        return obj.likes.filter(is_deleted=False).count()


class DiaryDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    images = serializers.SerializerMethodField()
    emotion = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "updated_at",
            "images",
            "emotion",
            "comments",
            "like_count",
        ]

    def get_images(self, obj):
        return [
            {"id": img.id, "image_url": img.image.url}
            for img in obj.images.filter(is_deleted=False)
        ]

    def get_emotion(self, obj):
        diary_emotion = getattr(obj, "emotion", None)
        if diary_emotion:
            return EmotionSerializer(diary_emotion.emotion).data
        return None

    def get_comments(self, obj):
        comments = obj.comments.filter(is_deleted=False)
        result = []
        for c in comments:
            result.append(
                {
                    "comment_id": c.id,
                    "user": UserSerializer(c.user).data,
                    "content": c.content,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "like_count": c.likes.filter(is_deleted=False).count(),
                }
            )
        return result

    def get_like_count(self, obj):
        return obj.likes.filter(is_deleted=False).count()


class CommentLikeToggleSerializer(serializers.ModelSerializer):
    """
    댓글 좋아요 토글 응답 직렬화기
    """

    class Meta:
        model = CommentLike
        fields = ["id"]


class DiaryLikeToggleSerializer(serializers.ModelSerializer):
    """
    다이어리 좋아요 토글 응답 직렬화기
    """

    class Meta:
        model = Like
        fields = ["id"]
