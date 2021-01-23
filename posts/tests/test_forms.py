import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.forms import PostForm

USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'
INDEX_URL = reverse('index')
NEW_POST = reverse('new_post')

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif')


class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = User.objects.create_user(
            username=USERNAME)
        cls.group = Group.objects.create(
            slug=SLUG)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=TEXT,
            )
        cls.form = PostForm()
        cls.POST_URL = (
            reverse('post',
                    args=[cls.author.username, cls.post.id]))
        cls.POST_EDIT_URL = (
            reverse('post_edit',
                    args=[cls.author.username, cls.post.id]))
        cls.expected_redirect_new = f'/auth/login/?next={NEW_POST}'
        cls.expected_redirect_edit = f'/auth/login/?next={cls.POST_EDIT_URL}'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostForm.author)

    def test_create_post_auth(self):
        '''Валидная форма создает запись в Post'''
        posts_count = Post.objects.count()
        form_data = {
            'author': TestPostForm.post.author,
            'text': TestPostForm.post.text,
            'group': TestPostForm.group.id,
            'image': UPLOADED}
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True)
        self.assertRedirects(response, INDEX_URL)
        # Количество постов увеличилось на один
        self.assertEqual(Post.objects.count(), posts_count+1)
        # Исключаю пост, созданный в классе
        post = Post.objects.exclude(id=self.post.id)
        # созданный в тесте пост существует
        self.assertTrue(post.exists())
        self.assertEqual(post[0].author, form_data['author'])
        self.assertEqual(post[0].text, form_data['text'])
        self.assertEqual(post[0].group.id, form_data['group'])
        self.assertEqual(
            post[0].image.file.read(),
            form_data['image'].file.getvalue())

    def test_create_post_guest(self):
        '''Гостевой акк не создает запись в Post'''
        posts_count = Post.objects.count()
        form_data = {
            'author': TestPostForm.post.author,
            'text': TestPostForm.post.text,
            'group': TestPostForm.group.id,
            'image': UPLOADED}
        response = self.guest_client.post(
            NEW_POST,
            data=form_data,
            follow=True)
        # Редирект на страницу логина
        self.assertRedirects(response, TestPostForm.expected_redirect_new)
        # Количество постов не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Исключаю пост, созданный в классе
        post = Post.objects.exclude(id=self.post.id)
        # Пост не создался
        self.assertFalse(post.exists())

    def test_edit_post_auth(self):
        '''Валидная форма изменяет запись в Post'''
        posts_count = Post.objects.count()
        form_data = {
            'text': TestPostForm.post.text,
            'group': TestPostForm.group.id}
        response = self.authorized_client.post(
            TestPostForm.POST_EDIT_URL,
            data=form_data,
            follow=True)
        # Пост с указанными данными существует
        post = Post.objects.filter(id=self.post.id)
        self.assertTrue(post.exists())
        # Постов с другими данными не существует
        not_post = Post.objects.exclude(id=self.post.id)
        self.assertFalse(not_post.exists())
        # Редирект происходит на страницу поста
        self.assertRedirects(response, TestPostForm.POST_URL)
        # Количество постов осталось прежним
        self.assertEqual(Post.objects.count(), posts_count)
        # Данные изменились
        self.assertEqual(post[0].text, form_data['text'])
        self.assertEqual(post[0].group.id, form_data['group'])

    def test_edit_post_guest(self):
        '''Гостевой акк не может добавить запись в Post'''
        form_data = {
            'text': '1234',
            'group': 2}
        response = self.guest_client.post(
            TestPostForm.POST_EDIT_URL,
            data=form_data,
            follow=True)
        # Пост с указанными данными существует
        post = Post.objects.filter(id=self.post.id)
        self.assertTrue(post.exists())
        # Постов с другими данными не существует
        not_post = Post.objects.exclude(id=self.post.id)
        self.assertFalse(not_post.exists())
        # Редирект на страницу логина
        self.assertRedirects(
            response, TestPostForm.expected_redirect_edit)
        # Содержимое поста не изменилось
        self.assertNotEqual(post[0].text, form_data['text'])
        self.assertNotEqual(post[0].group.id, form_data['group'])

