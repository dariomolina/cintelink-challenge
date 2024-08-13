from rest_framework.routers import DefaultRouter

from notification.views import NotificationViewSet, TagViewSet, NotificationSubscriptionViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'subscriptions', NotificationSubscriptionViewSet)

urlpatterns = router.urls
