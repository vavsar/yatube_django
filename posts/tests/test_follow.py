from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post, User

USERNAME1 = 'TestUser_01'
USERNAME2 = 'TestUser_02'
SLUG = 'test_slug'
TEXT = 'test_text'
INDEX_URL = reverse('index')
FOLLOW_INDEX = reverse('follow_index')
PROFILE_UNFOLLOW = reverse(
    'profile_unfollow',
    args=[USERNAME2])
PROFILE_FOLLOW = reverse(
            'profile_follow',
            args=[USERNAME1])


# тест подписывания пользователей друг на друга
class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create(
            username=USERNAME1)
        cls.user_not_follower = User.objects.create(
            username=USERNAME2)
        cls.post_not_follower = Post.objects.create(
            text=TEXT, author=cls.user_not_follower)
        cls.post_follower = Post.objects.create(
            text=TEXT, author=cls.user_follower)
        cls.following = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user_not_follower)
        cls.auth_client_follower = Client()
        cls.auth_client_follower.force_login(FollowTest.user_follower)
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(FollowTest.user_not_follower)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        self.assertTrue(Follow.objects.filter(
            user=FollowTest.user_follower,
            author=FollowTest.user_not_follower).exists)

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        FollowTest.following.delete()
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower, author=self.user_not_follower))

    def test_follower_post_added_to_follow(self):
        """Проверка, добавился ли пост подписчика"""
        response_follower = self.auth_client_follower.get(
            FOLLOW_INDEX)
        self.assertIn(FollowTest.post_not_follower,
                      response_follower.context['page'])

    def test_author_post_not_added_to_follow(self):
        """Проверка, добавился ли пост автора"""
        response_not_follower = self.auth_client_author.get(
            FOLLOW_INDEX)
        self.assertNotIn(FollowTest.post_not_follower,
                         response_not_follower.context['page'])

