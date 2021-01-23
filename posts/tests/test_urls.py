from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'
URL_404 = reverse('not_found')
URL_500 = reverse('server_error')
ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')
FOLLOW_INDEX = reverse("follow_index")
NEW_POST = reverse('new_post')
GROUP_SLUG_URL = (reverse('group_slug', args=[SLUG]))
INDEX_URL = reverse('index')
PROFILE = reverse('profile', args=[USERNAME])


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=USERNAME)
        cls.other = User.objects.create_user(
            username='other')
        cls.group = Group.objects.create(slug=SLUG, title='test_title')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
        )
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.POST_EDIT_URL = (
            reverse('post_edit',
                    args=[cls.post.author.username, cls.post.id]))
        cls.ADD_COMMENT = reverse(
            'add_comment', args=[cls.post.author.username, cls.post.id])
        cls.REDIR_POST_EDIT = f'/auth/login/?next={PostURLTests.POST_EDIT_URL}'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTests.author)

    def test_static_urls_status_code_and_template(self):
        templates_url_names = (
            (ABOUT_AUTHOR, self.guest_client, 200),
            (ABOUT_AUTHOR, self.authorized_client_author, 200),
            (ABOUT_TECH, self.guest_client, 200),
            (ABOUT_TECH, self.authorized_client_author, 200),
            (URL_404, self.guest_client, 404),
            (URL_404, self.authorized_client_author, 404),
            (URL_500, self.guest_client, 500),
            (URL_500, self.authorized_client_author, 500),
        )
        for reverse_name, client, status_code in templates_url_names:
            with self.subTest():
                response = response = client.get(reverse_name)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = (
            (URL_404, self.guest_client, 'misc/404.html'),
            (URL_404, self.authorized_client_author, 'misc/404.html'),
            (URL_500, self.guest_client, 'misc/500.html'),
            (URL_500, self.authorized_client_author, 'misc/500.html'),
            (ABOUT_AUTHOR, self.guest_client, 'about/author.html'),
            (ABOUT_AUTHOR, self.authorized_client_author, 'about/author.html'),
            (ABOUT_TECH, self.guest_client, 'about/tech.html'),
            (ABOUT_TECH, self.authorized_client_author, 'about/tech.html'),
            (FOLLOW_INDEX, self.authorized_client_author, 'follow.html'),
            (NEW_POST, self.authorized_client_author, 'post_edit.html'),
            (GROUP_SLUG_URL, self.guest_client, 'group.html'),
            (GROUP_SLUG_URL, self.authorized_client_author, 'group.html'),
            (INDEX_URL, self.guest_client, 'index.html'),
            (INDEX_URL, self.authorized_client_author, 'index.html'),
            (PROFILE, self.guest_client, 'profile.html'),
            (PROFILE, self.authorized_client_author, 'profile.html'),
            (PostURLTests.POST_URL,
                self.guest_client, 'post.html'),
            (PostURLTests.POST_URL,
                self.authorized_client_author, 'post.html'),
            (PostURLTests.POST_EDIT_URL,
                self.authorized_client_author, 'post_edit.html'),
            (PostURLTests.ADD_COMMENT,
                self.authorized_client_author, 'includes/comments.html'),
        )
        for reverse_name, client, template in templates_url_names:
            with self.subTest():
                response = response = client.get(reverse_name)
                self.assertTemplateUsed(response, template)
