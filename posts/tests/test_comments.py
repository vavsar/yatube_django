from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User, Comment

USERNAME = 'author'
USERNAME_2 = 'other'
SLUG = 'test_slug'
TEXT = 'test_text'
LOGIN = reverse('login')


class TestComments(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.author = User.objects.create_user(
            username=USERNAME)
        cls.other = User.objects.create_user(
            username=USERNAME_2)
        cls.group = Group.objects.create(
            slug=SLUG)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=TEXT,
            )
        cls.POST_URL = (
            reverse('post',
                    args=[USERNAME, cls.post.id]))
        cls.ADD_COMMENT = reverse(
            'add_comment',
            args=[USERNAME, cls.post.id])
        cls.REDIR_LOGIN_TO_ADD_COMM = (
            f'{LOGIN}?next={TestComments.ADD_COMMENT}')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(TestComments.author)
        self.authorized_client_other = Client()
        self.authorized_client_other.force_login(TestComments.other)

    def test_auth_user_can_post_comments(self):
        form_data = {
            'text': '1234'
            }
        response = self.authorized_client_other.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True)
        self.assertEqual(len(response.context['comments']), 1)
        new_comment = response.context['comments'][0]
        self.assertEqual(new_comment.author, self.other)
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.post, self.post)

    def test_guest_user_cant_post_comments(self):
        comments_count = Comment.objects.count()
        form_data = {'text': '1234'}
        response = self.guest_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True)
        self.assertRedirects(response, self.REDIR_LOGIN_TO_ADD_COMM)
        self.assertEqual(comments_count, Comment.objects.count())
