import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

MEDIA_ROOT = tempfile.mkdtemp()
USERNAME = 'author'
SLUG = 'test_slug'
TEXT = 'test_text'
URL_404 = reverse('not_found')
URL_500 = reverse('server_error')
ABOUT_AUTHOR = reverse('about:author')
ABOUT_TECH = reverse('about:tech')
FOLLOW_INDEX = reverse("follow_index")
NEW_POST = reverse('new_post')
GROUP_SLUG_URL = (reverse('group_slug', args=[SLUG]))
INDEX_URL = reverse('index')
PROFILE = reverse('profile', args=[USERNAME])


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
            )
        cls.POST_URL = (
            reverse('post',
                    args=[cls.post.author.username, cls.post.id]))
        cls.POST_URL_EDIT = (
            reverse('post_edit',
                    args=[cls.post.author.username, cls.post.id]))
        cls.ADD_COMMENT = reverse(
            'add_comment', args=[cls.post.author.username, cls.post.id])
        cls.posts = Post.objects.bulk_create([
            Post(
                author=PostPagesTest.author,
                group=PostPagesTest.group,
                text=TEXT,
            ) for i in range(20)
        ])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostPagesTest.author)

    def test_index_show_correct_context(self):
        response = self.guest_client.get(INDEX_URL)
        post_author = response.context.get('page')[0].author.username
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_author, PostPagesTest.author.username)
        self.assertEqual(post_group, PostPagesTest.group)

    def test_group_post_show_correct_context(self):
        '''Шаблон group_slug сформирован с правильным контекстом.'''
        response = self.guest_client.get(GROUP_SLUG_URL)
        self.assertEqual(response.context.get('group').slug, 'test_slug')

    def test_new_post_show_correct_context(self):
        '''Шаблон new_post сформирован с правильным контекстом.'''
        response = self.authorized_client_author.get(NEW_POST)
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_correct_context(self):
        response = self.authorized_client_author.get(
            PostPagesTest.POST_URL_EDIT
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_view_page_correct_context(self):
        response = self.authorized_client_author.get(
            PostPagesTest.POST_URL)
        self.assertEqual(
            response.context.get('post').author, PostPagesTest.author)
        self.assertEqual(
            response.context.get('post').group, PostPagesTest.group)
        self.assertEqual(
            response.context.get('post').text, 'test_text')

    def test_index_page_paginator_posts_count_correct(self):
        response = self.authorized_client_author.get(INDEX_URL)
        self.assertEqual(len(response.context['page']), 10)
        self.assertEqual(
            response.context['page'][0].group.title, PostPagesTest.group.title)

    def test_profile_show_correct_context(self):
        response = self.authorized_client_author.get(PROFILE)
        post_author = response.context.get('page')[0].author.username
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_author, 'author')
        self.assertEqual(post_group, PostPagesTest.group)


# class CacheTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.author = User.objects.create_user(
#             username=USERNAME)
#         cls.group = Group.objects.create(
#             slug=SLUG)
#         cls.post = Post.objects.create(
#             author=cls.author,
#             group=cls.group,
#             text=TEXT,
#             )

#     def setUp(self):
#         self.guest_client = Client()
#         self.authorized_client_author = Client()
#         self.authorized_client_author.force_login(CacheTest.author)

#     def test_cache(self):
#         response = self.authorized_client_author.get(reverse('index'))
#         Post.objects.create(
#             author=User.objects.create_user(
#                 username='new_author'),
#             group=Group.objects.create(
#                 slug='new_slug'),
#             text='NEW_TEXT',
#             )
#         response2 = self.authorized_client_author.get(reverse('index'))
#         self.assertEqual(response.content, response2.content)
#         cache.clear()
#         response3 = self.authorized_client_author.get(reverse('index'))
#         self.assertNotEqual(response.content, response3.content)
