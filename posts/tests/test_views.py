import shutil

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'
ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')
FOLLOW_INDEX = reverse('follow_index')
NEW_POST = reverse('new_post')
GROUP_SLUG_URL = (reverse('group_slug', args=[SLUG]))
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
        cls.group = Group.objects.create(
            slug=SLUG)
        cls.post = Post.objects.create(
            author=cls.author,
            text=TEXT,
            group=cls.group,
            image=UPLOADED,
            )
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.POST_URL_EDIT = (
            reverse('post_edit',
                    args=[cls.post.author.username, cls.post.id]))
        cls.ADD_COMMENT = reverse(
            'add_comment', args=[cls.post.author.username, cls.post.id])
        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(PostPagesTest.author)

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
        self.assertEqual(len(response.context['page']), 10)

    def test_correct_context_with_page(self):
        test_pages = (
            GROUP_SLUG_URL,
            PROFILE,
        )
        for url_name in test_pages:
            with self.subTest(url_name):
                response = self.authorized_client_author.get(url_name)
                response_post_context = response.context['page']
                self.assertEqual(len(response_post_context), 1)
                self.assertEqual(response_post_context[0], self.post)

    def test_correct_context_with_post(self):
        test_pages = (
            INDEX_URL,
            PostPagesTest.POST_URL,
        )
        for url_name in test_pages:
            with self.subTest(url_name):
                response = self.authorized_client_author.get(url_name)
                response_post_context = response.context['post']
                self.assertEqual(response_post_context, self.post)

    def test_author_for_profile_and_post_pages(self):
        test_pages = (
            PROFILE,
            PostPagesTest.POST_URL,
        )
        for url_name in test_pages:
            with self.subTest(url_name):
                response = self.authorized_client_author.get(url_name)
                response_context = response.context['post']
                self.assertEqual(response_context.author, self.post.author)


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
