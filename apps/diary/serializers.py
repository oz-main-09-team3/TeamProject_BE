# serializers.py
from rest_framework import serializers

from apps.diary.models import Diary, DiaryImage, Emotion


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
    images = DiaryImageSerializer(source='diaryimage_set', many=True, read_only=True)
    emotion = serializers.SerializerMethodField()

    class Meta:
        model = Diary
        fields = ['id', 'content', 'created_at', 'updated_at', 'visibility', 'images', 'emotion']

    def get_emotion(self, obj):
        emotion = Emotion.objects.filter(diary=obj).first()
        if emotion:
            return {
                'emoji': emotion.emoji,
                'emotion': emotion.emotion
            }
        return None


class CalendarDiarySerializer(serializers.Serializer):
    date = serializers.DateField()
    emotion = serializers.CharField(allow_null=True)
    emoji = serializers.CharField(allow_null=True)
    diary_id = serializers.IntegerField()