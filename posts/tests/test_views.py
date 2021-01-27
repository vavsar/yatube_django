import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User, Follow

PER_PAGE = settings.PER_PAGE
USERNAME = 'author'
USERNAME_2 = 'new_user'
SLUG = 'test_slug'
SLUG_2 = 'slug_2'
TEXT = 'test_text'
ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')
FOLLOW_INDEX = reverse('follow_index')
NEW_POST = reverse('new_post')
GROUP_SLUG_URL = (reverse('group_slug', args=[SLUG]))
GROUP_SLUG_2_URL = (reverse('group_slug', args=[SLUG_2]))
INDEX_URL = reverse('index')
PROFILE = reverse('profile', args=[USERNAME])
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


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username=USERNAME)
        cls.other = User.objects.create_user(
            username=USERNAME_2)
        cls.group = Group.objects.create(
            slug=SLUG)
        cls.group_2 = Group.objects.create(
            slug=SLUG_2)
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT,
            group=cls.group,
            image=UPLOADED,
            )
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(PostPagesTest.author)
        cls.authorized_client_other = Client()
        cls.authorized_client_other.force_login(PostPagesTest.other)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_index_page_paginator_posts_count_correct(self):
        Post.objects.bulk_create([
            Post(
                author=self.author,
                group=self.group,
                text=TEXT,
            ) for i in range(10)
        ])
        response = self.authorized_client_author.get(INDEX_URL)
        self.assertEqual(len(response.context['page']), PER_PAGE)

    def test_correct_context_post(self):
        Follow.objects.create(
            user=self.other,
            author=self.author
        )
        test_pages = (
            (INDEX_URL, self.guest_client),
            (FOLLOW_INDEX, self.authorized_client_other),
            (PostPagesTest.POST_URL, self.authorized_client_author),
            (PROFILE, self.authorized_client_author),
            (GROUP_SLUG_URL, self.authorized_client_author),
        )
        for url_name, client in test_pages:
            with self.subTest(url_name):
                response_context = client.get(url_name).context
                if 'post' in response_context:
                    self.assertEqual(self.post, response_context['post'])
                else:
                    self.assertIn(self.post, response_context['page'])

    def test_correct_context_author(self):
        test_pages = (
            PostPagesTest.POST_URL,
            PROFILE,
        )
        for url_name in test_pages:
            with self.subTest(url_name):
                response_context = (
                    self.authorized_client_author.get(url_name).context)
                self.assertEqual(
                    self.post.author, response_context['author'])

    def test_post_gets_into_right_group(self):
        test_post = Post.objects.create(
            author=self.author,
            text='wonderful_text',
            group=self.group_2,
        )
        response_profile = self.authorized_client_author.get(GROUP_SLUG_URL)
        self.assertNotIn(test_post, response_profile.context['page'])


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_cache(self):
        response = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            author=User.objects.create_user(
                username='new_author'),
            text='NEW_TEXT',
            )
        response2 = self.guest_client.get(INDEX_URL)
        self.assertEqual(response.content, response2.content)
        cache.clear()
        response3 = self.guest_client.get(INDEX_URL)
        self.assertNotEqual(response.content, response3.content)
