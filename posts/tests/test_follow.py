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
        cls.auth_client_not_follower = Client()
        cls.auth_client_not_follower.force_login(FollowTest.user_not_follower)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        recordings_count = Follow.objects.count()
        response = self.auth_client_not_follower.get(PROFILE_FOLLOW)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), recordings_count+1)

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        recordings_count = Follow.objects.count()
        response = self.auth_client_follower.get(PROFILE_UNFOLLOW)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), recordings_count-1)

    def test_follower_post_added_to_follow(self):
        """Проверка, добавился ли пост подписчика"""
        response_follower = self.auth_client_follower.get(
            FOLLOW_INDEX)
        # Получаю пост подписчика из фикстур
        expected_post = FollowTest.post_not_follower
        # Получаю пост подписчика из контекста
        actual_post = response_follower.context["page"][0]
        # Магия: посты не равны и не найден в контексте 'page'
        # AssertionError: <Post: test_text> != <Post: test_text>
        self.assertEqual(expected_post, actual_post)
        self.assertIn(expected_post,
                      response_follower.context['page'])

    def test_author_post_not_added_to_follow(self):
        """Проверка, добавился ли пост автора"""
        response_not_follower = self.auth_client_not_follower.get(
            FOLLOW_INDEX)
        # Получаю пост не-подписчика из фикстур
        expected_post = FollowTest.post_not_follower
        # Получаю пост не подписчика из контекста
        actual_post = response_not_follower.context["page"]
        # Магия: посты не равны
        self.assertNotEqual(expected_post, actual_post)
        self.assertNotIn(FollowTest.post_not_follower,
                         response_not_follower.context['page'])

