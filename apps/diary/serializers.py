# serializers.py
from rest_framework import serializers

from apps.diary.models import Diary, DiaryImage, Emotion
# from apps.user.models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'nickname', 'profile_image']

class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = ['id', 'content', 'created_at', 'updated_at', 'visibility']

class DiaryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryImage
        fields = ['id', 'image_url']

class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = ['id', 'emoji', 'emotion']

class DiaryDetailSerializer(serializers.ModelSerializer):
    images = DiaryImageSerializer(source='images', many=True, read_only=True)
    emotion = serializers.SerializerMethodField()
    # user = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = ['id', 'user', 'content', 'visibility', 'created_at', 'updated_at', 'images', 'emotion', 'comments', 'like_count']

    def get_emotion(self, obj):
        diary_emotion = getattr(obj, 'emotion', None)
        if diary_emotion:
            return EmotionSerializer(diary_emotion.emotion).data
        return None

    def get_like_count(self, obj):
        return obj.likes.filter(is_deleted=False).count()

    def get_comments(self, obj):
        comments = obj.comments.filter(is_deleted=False)
        return [{'comment_id': c.id, 'user_id': c.user.id, 'content': c.content, 'created_at': c.created_at,
                 'updated_at': c.updated_at} for c in comments]


class CalendarDiarySerializer(serializers.Serializer):
    date = serializers.DateField()
    emotion_id = serializers.IntegerField(allow_null=True)
    emoji = serializers.CharField(allow_null=True)
    diary_id = serializers.IntegerField()