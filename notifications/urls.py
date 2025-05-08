from rest_framework.routers import DefaultRouter

from notifications.apis import NotificationViewSet

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notifications")

urlpatterns = router.urls
