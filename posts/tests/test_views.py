import shutil
import tempfile

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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostPagesTest.author)

    def test_index_page_paginator_posts_count_correct(self):
        Post.objects.bulk_create([
            Post(
                author=PostPagesTest.author,
                group=PostPagesTest.group,
                text=TEXT,
            ) for i in range(10)
        ])
        response = self.authorized_client_author.get(INDEX_URL)
        self.assertEqual(len(response.context['page']), 10)
        self.assertEqual(
            response.context['page'][0].group.title, PostPagesTest.group.title)

    def test_correct_context(self):
        test_pages = [
            INDEX_URL,
            GROUP_SLUG_URL,
            PROFILE,
            PostPagesTest.POST_URL,
        ]
        for url_name in test_pages:
            with self.subTest(url_name=url_name):
                response = self.authorized_client_author.get(url_name)
                if "post" in response.context:
                    response_context = response.context["post"]
                else:
                    response_context = response.context["page"][0]
                expect_context = self.post
                self.assertEqual(response_context, expect_context)


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

