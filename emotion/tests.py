from datetime import datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.test import APIClient

from emotion.models import Emotion, EmotionData


class EmotionTestCase(TestCase):
    def setUp(self):
        # 테스트할 때 사용할 Emotion 객체를 미리 만든다.
        self.em = Emotion.objects.create(
            emoji="http://example.com/emoji.png",
            emotion="happy",
        )

    def test_str_method(self):
        """
        __str__()가
        'emoji URl - emotion' 형태로 나오는지 확인
        """
        expected = "http://example.com/emoji.png - happy"
        self.assertEqual(str(self.em), expected)

    def tset_field_max_length(self):
        """
        emoji 필드 max_length=255,
        emotion 필드 max_length=10 이 잘 설정됐는지 확인
        """
        emoji_field = self.em._meta.get_field("emoji")
        emotion_field = self.em._meta.get_field("emotion")
        self.assertEqual(emoji_field.max_length, 255)
        self.assertEqual(emotion_field.max_length, 10)

    def test_model_creation(self):
        """
        데이터를 저장하고 다시 불러왔을 때
        DB에 정상적으로 값이 남아 있는지 확인
        """
        obj = Emotion.objects.get(pk=self.em.pk)
        self.assertEqual(obj.emoji, "http://example.com/emoji.png")
        self.assertEqual(obj.emotion, "happy")


class EmotionAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.emotion1 = Emotion.objects.create(emoji="😀", emotion="happy")
        self.emotion2 = Emotion.objects.create(emoji="😢", emotion="sad")

        now = timezone.now()
        yesterday = now - timedelta(days=1)

        EmotionData.objects.create(emotion=self.emotion1, created_at=now)
        EmotionData.objects.create(emotion=self.emotion1, created_at=yesterday)
        EmotionData.objects.create(emotion=self.emotion2, created_at=yesterday)

        self.from_date = (now - timedelta(days=2)).date().isoformat()
        self.to_date = now.date().isoformat()

    def test_emotion_trend_view(self):
        response = self.client.get(
            "/api/emotion/trend/", {"from": self.from_date, "to": self.to_date}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_emotion_count_view(self):
        response = self.client.get(
            "/api/emotion/count/", {"from": self.from_date, "to": self.to_date}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

        emotion_ids = [self.emotion1.id, self.emotion2.id]
        for item in response.data:
            self.assertIn(item["emotion"], emotion_ids)
            self.assertIn("count", item)

    def test_missing_query_params(self):
        response = self.client.get("/api/emotion/trend/")
        self.assertEqual(response.status_code, 400)

        response = self.client.get("/api/emotion/count/")
        self.assertEqual(response.status_code, 400)
