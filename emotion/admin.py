from django.contrib import admin

from emotion.models import Emotion, EmotionData


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ["id", "emotion"]
    search_fields = ["emotion"]
    list_filter = ["emotion"]


@admin.register(EmotionData)
class EmotionDataAdmin(admin.ModelAdmin):
    list_display = ["id", "emotion", "created_at"]
    search_fields = ["emotion__emotion"]
    list_filter = ["created_at"]
