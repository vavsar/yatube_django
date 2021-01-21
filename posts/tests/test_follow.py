from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post


# тест подписывания пользователей друг на друга
class FollowUserViewTest(TestCase):

    def setUp(self):
        # создадим 2х пользователей.
        self.user_follower = get_user_model().objects.create(
            username='TestUser_01')
        self.user_not_follower = get_user_model().objects.create(
            username='TestUser_02')
        # Создадим 2 записи на нашем сайте
        Post.objects.create(
            text='test_text', author=self.user_not_follower)
        Post.objects.create(
            text='test_text', author=self.user_follower)
        # авторизуем подписчика
        self.auth_client_follower = Client()
        self.auth_client_follower.force_login(self.user_follower)
        # авторизуем владельца записи на нашем сайте
        self.auth_client_author = Client()
        self.auth_client_author.force_login(self.user_not_follower)

    def test_authorized_user_follow_to_other_user(self):
        """Тестирование подписывания на пользователей"""
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={'username': self.user_not_follower}))
        self.assertTrue(Follow.objects.filter(
            user=self.user_follower, author=self.user_not_follower),
                        'Подписка на пользователя не рабоатет')

    def test_authorized_user_unfollow(self):
        """Тестирование отписывания от пользователей"""
        self.auth_client_follower.get(reverse(
            'profile_unfollow',
            kwargs={'username': self.user_not_follower}))
        self.assertFalse(Follow.objects.filter(
            user=self.user_follower, author=self.user_not_follower),
                         'Отписка от пользователя не работает')

    def test_post_added_to_follow(self):
        """Тестирование на правильность работы подписывания на пользователя"""
        # подпишем пользователя на auth_client_author
        self.auth_client_follower.get(reverse(
            'profile_follow',
            kwargs={'username': self.user_not_follower}))
        # получим все посты подписанного пользователя
        posts = Post.objects.filter(
            author__following__user=self.user_follower)
        response_follower = self.auth_client_follower.get(
            reverse('follow_index'))
        response_author = self.auth_client_author.get(
            reverse('follow_index'))
        # проверим содержание Context страницы follow_index пользователя
        # auth_client_follower и убедимся, что они имеются в ленте
        self.assertIn(posts.get(),
                      response_follower.context['page'].object_list,
                      'Запись отсутствует на странице подписок пользователя')
        # проверим содержание Context страницы follow_index пользователя
        # auth_client_author и убедимся, что записи в ленте не имеется
        self.assertNotIn(posts.get(),
                         response_author.context['page'].object_list,
                         'Запись добавлена к неверному пользователю.')
