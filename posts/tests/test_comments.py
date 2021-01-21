from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = get_user_model().objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_text',
            )
        cls.REVERSE_ADD_COMMENTS = reverse(
            ('add_comment'), kwargs={
                'username': 'author', 'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(TestComments.author)

    def test_only_auth_user_can_access_comments(self):
        response_guest = self.guest_client.get(
            TestComments.REVERSE_ADD_COMMENTS, follow=True)
        response_author = self.authorized_client_author.get(
            TestComments.REVERSE_ADD_COMMENTS, follow=True)
        self.assertRedirects(response_guest, (
            f'/auth/login/?next={TestComments.REVERSE_ADD_COMMENTS}')
        )
        self.assertEqual(response_author.status_code, 200)
