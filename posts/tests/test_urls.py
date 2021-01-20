from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_accessible(self):
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_template(self):
        '''Проверка шаблона для адреса /about/about/.'''
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')

    def test_error_urls_uses_correct_template(self):
        response = self.guest_client.get(reverse('not_found'))
        self.assertTemplateUsed(response, 'misc/404.html')
        response = self.guest_client.get(reverse('server_error'))
        self.assertTemplateUsed(response, 'misc/500.html')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = get_user_model().objects.create_user(
            username='author')
        cls.other = get_user_model().objects.create_user(
            username='other')
        cls.group = Group.objects.create(slug='test_slug', title='test_title')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
        )
        cls.REVERSE_URL_INDEX = reverse('index')
        cls.REVERSE_URL_GROUP_SLUG = (
            reverse('group_slug', kwargs={'slug': 'test_slug'}))
        cls.REVERSE_NEW_POST = reverse('new_post')
        cls.REVERSE_URL_POST = (
            reverse('post',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))
        cls.REVERSE_URL_POST_EDIT = (
            reverse('post_edit',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))
        cls.REVERSE_PROFILE = reverse(
            'profile', kwargs={'username': 'author'})

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент
        self.authorized_client_author = Client()
        self.authorized_client_other = Client()
        self.authorized_client_author.force_login(PostURLTests.author)
        self.authorized_client_other.force_login(PostURLTests.other)

    def test_home_list_url_exists_at_desired_location(self):
        '''Страница 'index' доступна любому пользователю.'''
        response = self.guest_client.get(PostURLTests.REVERSE_URL_INDEX)
        self.assertEqual(response.status_code, 200)

    def test_group_url_exists_at_desired_location(self):
        '''Страница /group/test-slug/ доступна любому пользователю.'''
        response = self.guest_client.get(
            PostURLTests.REVERSE_URL_GROUP_SLUG)
        self.assertEqual(response.status_code, 200)

    def test_new_url_exists_at_desired_location(self):
        '''Страница /new/ доступна авторизованному пользователю.'''
        response = self.authorized_client_author.get(
            PostURLTests.REVERSE_NEW_POST)
        self.assertEqual(response.status_code, 200)

    def test_profile_url_exists_at_desired_location(self):
        '''Страница 'profile' доступна любому пользователю.'''
        response = self.guest_client.get(PostURLTests.REVERSE_PROFILE)
        self.assertEqual(response.status_code, 200)

    def test_username_single_post_url_exists_at_desired_location(self):
        '''Страница 'post' доступна любому пользователю.'''
        response = self.guest_client.get(PostURLTests.REVERSE_URL_POST)
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location(self):
        '''Страница редактирования поста доступна автор. пользователю.'''
        response_guest = self.guest_client.get(
            PostURLTests.REVERSE_URL_POST_EDIT, follow=True)
        response_other = self.authorized_client_other.get(
            PostURLTests.REVERSE_URL_POST_EDIT, follow=True)
        response_author = self.authorized_client_author.get(
            PostURLTests.REVERSE_URL_POST_EDIT)
        self.assertRedirects(response_guest, (
            f'/auth/login/?next={PostURLTests.REVERSE_URL_POST_EDIT}'))
        self.assertRedirects(response_other, PostURLTests.REVERSE_NEW_POST)
        self.assertEqual(response_author.status_code, 200)
