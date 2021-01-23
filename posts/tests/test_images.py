import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp()
USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'
INDEX_URL = reverse('index')
NEW_POST = reverse('new_post')
GROUP_SLUG_URL = (reverse('group_slug', args=['test_slug']))
PROFILE = reverse('profile', args=['author'])
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )
UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PostImageViewTest(TestCase):
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
            text=TEXT,
            group=cls.group,
            image=UPLOADED)
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.POST_URL_EDIT = (
            reverse('post_edit',
                    args=[cls.post.author.username, cls.post.id]))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

    def test_context_index_page(self):
        """Проверяем context страницы index на наличие изображения"""
        response = self.guest_client.get(INDEX_URL)
        response_data_image = response.context['page'][0].image
        expected = f'posts/{UPLOADED.name}'
        self.assertEqual(response_data_image, expected)

    def test_profile_page_context(self):
        """Проверяем context страницы profile на наличие изображения"""
        response = self.guest_client.get(PROFILE)
        response_data_image = response.context['page'][0].image
        expected = f'posts/{UPLOADED.name}'
        self.assertEqual(response_data_image, expected)

    def test_group_post_page_context(self):
        """Проверяем context страницы group на наличие изображения"""
        response = self.guest_client.get(GROUP_SLUG_URL)
        response_data_image = response.context['page'][0].image
        expected = f'posts/{UPLOADED.name}'
        self.assertEqual(response_data_image, expected)

    def test_single_post_page_context(self):
        """Проверяем context страницы <post_id> на наличие изображения"""
        response = self.guest_client.get(PostImageViewTest.POST_URL)
        response_data_image = response.context['post'].image
        expected = f'posts/{UPLOADED.name}'
        self.assertEqual(response_data_image, expected)
