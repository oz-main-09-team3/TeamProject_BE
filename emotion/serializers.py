from rest_framework import serializers

from emotion.models import Emotion, EmotionData


class EmotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emotion
        fields = ["id", "emoji", "emotion"]
        read_only_fields = ["id"]


class EmotionTrendViewSerializer(serializers.ModelSerializer):
    emotion = EmotionSerializer()

    class Meta:
        model = EmotionData
        fields = ["emotion", "created_at"]
