from rest_framework import serializers

from emotion.models import Emotion, EmotionData


class EmotionSerializer(serializers.ModelSerializer):
    # image_url = serializers.SerializerMethodField()

    class Meta:
        model = Emotion
        fields = ["id", "emoji", "emotion", "image_url"]


class EmotionTrendViewSerializer(serializers.ModelSerializer):
    emotion = EmotionSerializer(read_only=True)

    class Meta:
        model = EmotionData
        fields = ["emotion", "created_at"]
