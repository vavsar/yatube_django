from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_text',
            )
        cls.ADD_COMMENTS = reverse(
            'add_comment',
            args=[cls.author.username, cls.post.id])
        cls.LOGIN = reverse('login')
        cls.LOGIN_REDIRECTS_TO_ADD_COMMENT = reverse(
            f'{cls.LOGIN}?next={cls.ADD_COMMENTS}')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(TestComments.author)

    def test_only_auth_user_can_access_comments(self):
        response_guest = self.guest_client.get(
            TestComments.ADD_COMMENTS, follow=True)
        response_author = self.authorized_client_author.get(
            TestComments.ADD_COMMENTS, follow=True)
        self.assertRedirects(response_guest, (
            TestComments.LOGIN_REDIRECTS_TO_ADD_COMMENT)
        self.assertEqual(response_author.status_code, 200)
