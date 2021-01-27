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
GROUP_SLUG_URL = reverse('group_slug', args=[SLUG])
INDEX_URL = reverse('index')
PROFILE = reverse('profile', args=[USERNAME])
LOGIN = reverse('login')
FOLLOW_REDIRECT = f'{LOGIN}?next={FOLLOW_INDEX}'
NEW_POST_REDIRECT = f'{LOGIN}?next={NEW_POST}'


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
        cls.REDIRECT_POST_EDIT = (
            f'{LOGIN}?next={PostURLTests.POST_EDIT_URL}')
        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(PostURLTests.author)

    def test_urls_status_code(self):
        URLS_LIST = (
            (ABOUT_AUTHOR, self.guest_client, 200),
            (ABOUT_AUTHOR, self.authorized_client_author, 200),
            (ABOUT_TECH, self.guest_client, 200),
            (ABOUT_TECH, self.authorized_client_author, 200),
            (URL_404, self.guest_client, 404),
            (URL_404, self.authorized_client_author, 404),
            (URL_500, self.guest_client, 500),
            (URL_500, self.authorized_client_author, 500),
            (FOLLOW_INDEX, self.authorized_client_author, 200),
            (NEW_POST, self.authorized_client_author, 200),
            (GROUP_SLUG_URL, self.guest_client, 200),
            (INDEX_URL, self.guest_client, 200),
            (PROFILE, self.guest_client, 200),
            (PostURLTests.POST_URL,
                self.guest_client, 200),
            (PostURLTests.POST_EDIT_URL,
                self.authorized_client_author, 200),
            (FOLLOW_INDEX, self.authorized_client_author, 200)
        )
        for url, client, status_code in URLS_LIST:
            with self.subTest():
                self.assertEqual(
                    client.get(url).status_code, status_code)

    def test_urls_uses_correct_template(self):
        URL_LIST = (
            (URL_404, self.guest_client, 'misc/404.html'),
            (URL_500, self.guest_client, 'misc/500.html'),
            (ABOUT_AUTHOR, self.guest_client, 'about/author.html'),
            (ABOUT_TECH, self.guest_client, 'about/tech.html'),
            (FOLLOW_INDEX, self.authorized_client_author, 'follow.html'),
            (NEW_POST, self.authorized_client_author, 'post_edit.html'),
            (GROUP_SLUG_URL, self.guest_client, 'group.html'),
            (INDEX_URL, self.guest_client, 'index.html'),
            (PROFILE, self.guest_client, 'profile.html'),
            (PostURLTests.POST_URL,
                self.guest_client, 'post.html'),
            (PostURLTests.POST_EDIT_URL,
                self.authorized_client_author, 'post_edit.html'),
        )
        for url, client, template in URL_LIST:
            with self.subTest():
                self.assertTemplateUsed(client.get(url), template)

    def test_urls_correct_redirect(self):
        URL_LIST = (
            (FOLLOW_INDEX, self.guest_client, FOLLOW_REDIRECT),
            (NEW_POST, self.guest_client, NEW_POST_REDIRECT),
            (PostURLTests.POST_EDIT_URL,
                self.guest_client, PostURLTests.REDIRECT_POST_EDIT),
        )
        for reverse_name, client, redirect in URL_LIST:
            with self.subTest():
                self.assertRedirects(client.get(reverse_name), redirect)
