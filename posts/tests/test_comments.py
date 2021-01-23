from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User, Comment

USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username=USERNAME)
        cls.group = Group.objects.create(
            slug=SLUG)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=TEXT,
            )
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.ADD_COMMENTS = reverse(
            'add_comment',
            args=[cls.author.username,
                  cls.post.id])
        cls.LOGIN = reverse('login')
        cls.REDIR_LOGIN_TO_ADD_COMM = (
            f'{TestComments.LOGIN}?next={TestComments.ADD_COMMENTS}')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(TestComments.author)

    def test_auth_user_can_post_comments(self):
        test_item = Comment.objects.create(
            author=TestComments.author,
            post=TestComments.post,
            text=TEXT
        )
        response_auth = self.authorized_client_author.get(
            TestComments.POST_URL)
        self.assertEqual(
            response_auth.context['comments'][0].author, test_item.author)
        self.assertEqual(
            response_auth.context['comments'][0].post, test_item.post)
        self.assertEqual(
            response_auth.context['comments'][0].text, test_item.text)

    def test_guest_user_cant_post_comments(self):
        test_item = Comment.objects.create(
            author=TestComments.author,
            post=TestComments.post,
            text=TEXT
        )
        obj = Comment.objects.filter(author=test_item.author)
        response_guest = self.guest_client.get(
            TestComments.POST_URL)
        self.assertNotIn(obj, response_guest.context['comments'])
