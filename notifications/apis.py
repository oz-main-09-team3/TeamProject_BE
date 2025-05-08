from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
