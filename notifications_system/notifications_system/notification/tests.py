from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.management import call_command

from notification.models import (
    Tag, Notification, NotificationSubscription, UserNotification
)
from notification.serializers import (
    TagSerializer, NotificationSerializer,
    NotificationSubscriptionSerializer, UserNotificationSerializer
)


class NotificationModelsTest(TestCase):

    def setUp(self):
        call_command('migrate', '--noinput')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.tag = Tag.objects.create(name='Test Tag')
        self.notification = Notification.objects.create(tag=self.tag, message='Test Notification')
        self.subscription = NotificationSubscription.objects.create(user=self.user, tag=self.tag)
        self.user_notification = UserNotification.objects.create(user=self.user, notification=self.notification)

    def test_tag_creation(self):
        self.assertEqual(self.tag.name, 'Test Tag')

    def test_notification_creation(self):
        self.assertEqual(self.notification.message, 'Test Notification')
        self.assertEqual(self.notification.tag, self.tag)

    def test_notification_subscription_creation(self):
        self.assertEqual(self.subscription.user, self.user)
        self.assertEqual(self.subscription.tag, self.tag)

    def test_user_notification_creation(self):
        self.assertEqual(self.user_notification.user, self.user)
        self.assertEqual(self.user_notification.notification, self.notification)
        self.assertFalse(self.user_notification.is_read)
        self.assertFalse(self.user_notification.is_deleted)


class NotificationSerializersTest(APITestCase):

    def setUp(self):
        call_command('migrate', '--noinput')
        self.tag = Tag.objects.create(name='Test Tag')
        self.notification = Notification.objects.create(tag=self.tag, message='Test Notification')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.subscription = NotificationSubscription.objects.create(user=self.user, tag=self.tag)
        self.user_notification = UserNotification.objects.create(user=self.user, notification=self.notification)

    def test_tag_serializer(self):
        serializer = TagSerializer(self.tag)
        self.assertEqual(serializer.data, {'id': self.tag.id, 'name': 'Test Tag'})

    def test_notification_serializer(self):
        serializer = NotificationSerializer(self.notification)
        self.assertEqual(serializer.data, {
            'id': self.notification.id,
            'tag': self.tag.id,
            'message': 'Test Notification',
            'timestamp': self.notification.timestamp.isoformat()
        })

    def test_notification_subscription_serializer(self):
        serializer = NotificationSubscriptionSerializer(self.subscription)
        self.assertEqual(serializer.data, {
            'id': self.subscription.id,
            'user': self.user.id,
            'tag': self.tag.id,
            'created_at': self.subscription.created_at.isoformat()
        })

    def test_user_notification_serializer(self):
        serializer = UserNotificationSerializer({
            'id': self.user_notification.id,
            'timestamp': self.user_notification.notification.timestamp,
            'is_read': self.user_notification.is_read,
            'message': self.user_notification.notification.message
        })
        self.assertEqual(serializer.data, {
            'id': self.user_notification.id,
            'timestamp': self.user_notification.notification.timestamp.isoformat(),
            'is_read': self.user_notification.is_read,
            'message': self.user_notification.notification.message
        })


class NotificationViewsTest(APITestCase):

    def setUp(self):
        call_command('migrate', '--noinput')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.tag = Tag.objects.create(name='Test Tag')
        self.notification = Notification.objects.create(tag=self.tag, message='Test Notification')

    def test_tag_viewset(self):
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notification_viewset(self):
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_notification(self):
        url = reverse('notification-list')
        data = {
            'tag': self.tag.id,
            'message': 'New Test Notification'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(message='New Test Notification').exists())

    def test_create_subscription(self):
        url = reverse('notificationsubscription-list')
        data = {
            'tag': self.tag.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(NotificationSubscription.objects.filter(user=self.user, tag=self.tag).exists())
