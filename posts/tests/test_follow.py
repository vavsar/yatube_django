from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post, User

USERNAME_1 = 'TestUser_01'
USERNAME_2 = 'TestUser_02'
SLUG = 'test_slug'
TEXT = 'test_text'
INDEX_URL = reverse('index')
FOLLOW_INDEX = reverse('follow_index')
PROFILE_FOLLOW = reverse(
    'profile_follow',
    args=[USERNAME_2])
PROFILE_UNFOLLOW = reverse(
    'profile_unfollow',
    args=[USERNAME_2])


# тест подписывания пользователей друг на друга
class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create(
            username=USERNAME_1)
        cls.user_author = User.objects.create(
            username=USERNAME_2)
        cls.post_not_follower = Post.objects.create(
            text=TEXT, author=cls.user_author)
        cls.post_follower = Post.objects.create(
            text=TEXT, author=cls.user_follower)
        cls.auth_client_follower = Client()
        cls.auth_client_follower.force_login(FollowTest.user_follower)
        cls.auth_client_author = Client()
        cls.auth_client_author.force_login(FollowTest.user_author)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        response = self.auth_client_follower.get(PROFILE_FOLLOW)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower,
            author=self.user_author).exists())

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_author)
        response = self.auth_client_follower.get(PROFILE_UNFOLLOW)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower,
            author=self.user_author).exists())

    def test_follower_post_added_to_follow(self):
        """Проверка, добавился ли пост подписчика"""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_author)
        response_follower = self.auth_client_follower.get(
            FOLLOW_INDEX)
        expected_post = self.post_not_follower
        self.assertIn(expected_post,
                      response_follower.context['page'])

    def test_author_post_not_added_to_follow(self):
        """Проверка, добавился ли пост автора"""
        response_not_follower = self.auth_client_author.get(
            FOLLOW_INDEX)
        self.assertNotIn(self.post_not_follower,
                         response_not_follower.context['page'])
