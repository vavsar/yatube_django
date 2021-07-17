from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='testuser')
        cls.post = Post.objects.create(
            text='01234567890123456789',
            author=cls.user,
        )

    def test_verbose(self):
        post = PostModelTest.post
        field_verboses = {
            'group': 'Группа',
            'text': 'Текст поста',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'group': 'Здесь группа',
            'text': 'Здесь текст поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_post_str(self):
        post = PostModelTest.post
        self.assertEquals(str(post), post.text[:15])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
        )

    def test_group_str(self):
        group = GroupModelTest.group
        self.assertEquals(str(group), group.title)
