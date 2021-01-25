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
                    args=[USERNAME, cls.post.id]))
        cls.ADD_COMMENT = reverse(
            'add_comment',
            args=[USERNAME,
                  cls.post.id])
        cls.LOGIN = reverse('login')
        cls.REDIR_LOGIN_TO_ADD_COMM = (
            f'{TestComments.LOGIN}?next={TestComments.ADD_COMMENT}')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(TestComments.author)

    def test_auth_user_can_post_comments(self):
        # Очищаю все комменты, чтобы новый был единственным
        Comment.objects.all().delete()
        comments_count = Comment.objects.count()
        form_data = {
            'text': '1234'
            }
        self.authorized_client_author.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True)
        new_comment = Comment.objects.get()
        self.assertNotEqual(comments_count, comments_count+1)
        self.assertEqual(new_comment.text, form_data['text'])
        self.assertEqual(new_comment.post, self.post)
        self.assertEqual(new_comment.author, self.post.author)

    def test_guest_user_cant_post_comments(self):
        comments_count = Comment.objects.count()
        form_data = {'text': '1234'}
        response = self.guest_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True)
        self.assertRedirects(response, self.REDIR_LOGIN_TO_ADD_COMM)
        self.assertEqual(comments_count, Comment.objects.count())
