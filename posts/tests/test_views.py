import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = get_user_model().objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_text',
            )
        cls.posts = Post.objects.bulk_create([
            Post(
                author=PostPagesTest.author,
                group=PostPagesTest.group,
                text='test_text',
            ) for i in range(20)
        ])
        cls.REVERSE_URL_INDEX = reverse('index')
        cls.REVERSE_URL_GROUP_SLUG = (
            reverse('group_slug', kwargs={'slug': 'test_slug'}))
        cls.REVERSE_NEW_POST = reverse('new_post')
        cls.REVERSE_URL_POST = (
            reverse('post',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))
        cls.REVERSE_URL_POST_EDIT = (
            reverse('post_edit',
                    kwargs={'username': 'author', 'post_id': cls.post.id}))
        cls.REVERSE_PROFILE = reverse(
            'profile', kwargs={'username': 'author'})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostPagesTest.author)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {
            'index.html': PostPagesTest.REVERSE_URL_INDEX,
            'group.html': PostPagesTest.REVERSE_URL_GROUP_SLUG,
            'new.html': PostPagesTest.REVERSE_NEW_POST,
            'post_edit.html': PostPagesTest.REVERSE_URL_POST_EDIT,
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        response = self.guest_client.get(PostPagesTest.REVERSE_URL_INDEX)
        post_author = response.context.get('page')[0].author.username
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_author, PostPagesTest.author.username)
        self.assertEqual(post_group, PostPagesTest.group)

    def test_group_post_show_correct_context(self):
        '''Шаблон group_slug сформирован с правильным контекстом.'''
        response = self.guest_client.get(
            PostPagesTest.REVERSE_URL_GROUP_SLUG)
        self.assertEqual(response.context.get('group').slug, 'test_slug')

    def test_new_post_show_correct_context(self):
        '''Шаблон new_post сформирован с правильным контекстом.'''
        response = self.authorized_client_author.get(
            PostPagesTest.REVERSE_NEW_POST)
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
            PostPagesTest.REVERSE_URL_POST_EDIT
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
            PostPagesTest.REVERSE_URL_POST)
        self.assertEqual(
            response.context.get('post').author, PostPagesTest.author)
        self.assertEqual(
            response.context.get('post').group, PostPagesTest.group)
        self.assertEqual(
            response.context.get('post').text, 'test_text')

    def test_index_page_paginator_posts_count_correct(self):
        response = self.authorized_client_author.get(
            PostPagesTest.REVERSE_URL_INDEX)
        self.assertEqual(len(response.context['page']), 10)
        self.assertEqual(
            response.context['page'][0].group.title, PostPagesTest.group.title)

    def test_profile_show_correct_context(self):
        response = self.authorized_client_author.get(
            PostPagesTest.REVERSE_PROFILE)
        post_author = response.context.get('page')[0].author.username
        post_group = response.context.get('page')[0].group
        self.assertEqual(post_author, 'author')
        self.assertEqual(post_group, PostPagesTest.group)


class PostImageViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                         b'\x01\x00\x80\x00\x00\x00\x00\x00'
                         b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                         b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                         b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                         b'\x0A\x00\x3B'
                         )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.author = get_user_model().objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text',
            group=cls.group,
            image=cls.uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()

    def test_context_index_page(self):
        """Проверяем context страницы index на наличие изображения"""
        response = self.guest_client.get(reverse('index'))
        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'
        self.assertEqual(response_data_image,
                         expected)

    def test_profile_page_context(self):
        """Проверяем context страницы profile на наличие изображения"""
        response = self.guest_client.get(reverse(
            'profile', kwargs={'username': 'author'}))
        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'
        self.assertEqual(response_data_image,
                         expected)

    def test_group_post_page_context(self):
        """Проверяем context страницы group на наличие изображения"""
        response = self.guest_client.get(reverse(
            'group_slug', kwargs={'slug': 'test_slug'}))
        response_data_image = response.context['page'][0].image
        expected = f'posts/{self.uploaded.name}'
        self.assertEqual(response_data_image,
                         expected)

    def test_single_post_page_context(self):
        """Проверяем context страницы <post_id> на наличие изображения"""
        response = self.guest_client.get(reverse(
            'post', kwargs={
                'username': 'author',
                'post_id': PostImageViewTest.post.id}))
        response_data_image = response.context['post'].image
        expected = f'posts/{PostImageViewTest.uploaded.name}'
        self.assertEqual(response_data_image, expected)
