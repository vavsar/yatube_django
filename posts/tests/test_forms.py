import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

USERNAME = 'author'
SLUG = 'test_slug'
SLUG_2 = 'slug_2'
TEXT = 'test_text'
INDEX_URL = reverse('index')
NEW_POST = reverse('new_post')
LOGIN = reverse('login')

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
        cls.group_2 = Group.objects.create(
            slug=SLUG_2)
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
        cls.expected_redirect_new = f'{LOGIN}?next={NEW_POST}'
        cls.expected_redirect_edit = f'{LOGIN}?next={cls.POST_EDIT_URL}'
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post_auth(self):
        form_data = {
            'text': 'new_text',
            'group': self.group.id,
            'image': UPLOADED}
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True)
        self.assertEqual(Post.objects.count(), 2)
        post = Post.objects.exclude(id=self.post.id)[0]
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(
            post.author, self.author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(
            post.image.file.read(),
            form_data['image'].file.getvalue())

    def test_create_post_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new_text',
            'group': self.group.id,
            'image': UPLOADED}
        response = self.guest_client.post(
            NEW_POST,
            data=form_data,
            follow=True)
        self.assertRedirects(response, TestPostForm.expected_redirect_new)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_auth(self):
        '''Валидная форма изменяет запись в Post'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new_text',
            'group': self.group_2.id,
            'image': UPLOADED}
        response = self.authorized_client.post(
            TestPostForm.POST_EDIT_URL,
            data=form_data)
        post_from_context = response.context['post']
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post_from_context.group.id, form_data['group'])
        self.assertEqual(post_from_context.text, form_data['text'])
        self.assertIsNotNone(post_from_context.image)

    def test_edit_post_guest(self):
        '''Гостевой акк не может добавить запись в Post'''
        form_data = {
            'text': 'double_new_text',
            'group': self.group.id,
            'image': UPLOADED}
        self.guest_client.post(
            TestPostForm.POST_EDIT_URL,
            data=form_data,
            follow=True)
        self.assertEqual(Post.objects.count(), 1)
        post_after = Post.objects.get()
        self.assertEqual(self.post, post_after)

    def test_new_post_show_correct_context(self):
        '''Шаблон new_post сформирован с правильным контекстом.'''
        URLS = (
            NEW_POST,
            TestPostForm.POST_EDIT_URL
        )
        for url in URLS:
            response = self.authorized_client.get(url)
            form_fields = {
                'group': forms.fields.ChoiceField,
                'text': forms.fields.CharField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)
