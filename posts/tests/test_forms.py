import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post
from posts.forms import PostForm


class TestPostForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.author = get_user_model().objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text',
            )
        cls.form = PostForm()
        cls.REVERSE_NEW_POST = reverse('new_post')
        cls.REVERSE_URL_POST = (
            reverse('post',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))
        cls.REVERSE_URL_POST_EDIT = (
            reverse('post_edit',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestPostForm.author)

    def test_create_post(self):
        '''Валидная форма создает запись в Post'''
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        form_data = {'text': '1234', 'image': uploaded}
        response = self.authorized_client.post(
            TestPostForm.REVERSE_NEW_POST,
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertEqual(Post.objects.filter(text='1234')[0].text, '1234')
        self.assertEqual(
            Post.objects.filter(text='1234')[0].image.file.read(),
            form_data['image'].file.getvalue())

    def test_edit_post(self):
        '''Валидная форма изменяет запись в Post'''
        posts_count = Post.objects.count()
        form_data = {'text': 'test_text'}
        response = self.authorized_client.post(
            TestPostForm.REVERSE_URL_POST_EDIT,
            data=form_data,
            follow=True)
        TestPostForm.post.refresh_from_db()
        # Количество постов осталось прежним
        self.assertEqual(
            Post.objects.count(), posts_count)
        # Текст поста не изменился
        self.assertEqual(TestPostForm.post.text, 'test_text')
        # Редирект на страницу поста с прежним id
        self.assertRedirects(response, TestPostForm.REVERSE_URL_POST)
