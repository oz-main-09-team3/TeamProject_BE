from django.db import migrations


def create_emotions(apps, schema_editor):
    Emotion = apps.get_model("diary", "Emotion")
    emotions = [
        {"emoji": "😊", "emotion": "행복"},
        {"emoji": "😢", "emotion": "슬픔"},
        {"emoji": "😡", "emotion": "화남"},
        {"emoji": "😴", "emotion": "피곤"},
        {"emoji": "😌", "emotion": "편안"},
        {"emoji": "😍", "emotion": "사랑"},
        {"emoji": "😱", "emotion": "놀람"},
        {"emoji": "😰", "emotion": "걱정"},
    ]
    for emotion_data in emotions:
        Emotion.objects.create(**emotion_data)


def remove_emotions(apps, schema_editor):
    Emotion = apps.get_model("diary", "Emotion")
    Emotion.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("diary", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_emotions, remove_emotions),
    ]
