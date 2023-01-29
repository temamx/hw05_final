from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Группа',
            slug='Слаг',
            description='Описание',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text="Не более 15 символов может уместиться в превью"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Короткий пост",
        )
        cls.comment = Comment.objects.create(
            author=cls.user_author,
            text='Тестовый комментарий',
        )
    
    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_model_post_have_correct_object_name(self):
        post = PostModelTest.post
        long_post = PostModelTest.long_post
        expected_post = post.text
        expected_long_post = long_post.text
        self.assertEqual(
            str(expected_long_post),
            "Не более 15 символов может уместиться в превью"
        )
        self.assertEqual(str(expected_post), "Короткий пост")

    def test_model_group_have_correct_object_name(self):
        group_str = Group.objects.get(pk=1)
        self.assertEqual(str(group_str), group_str.title)
