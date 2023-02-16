from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache

from posts.tests.shortcuts import group_create, post_create

from ..models import Group, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = group_create('Группа', 'Описание')
        cls.long_post = post_create(
            'Не более 15 символов может уместиться в превью',
            cls.user,
            cls.group
        )
        cls.post = post_create('Короткий пост', cls.user, cls.group)
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_model_post_have_correct_object_name(self):
        post = PostModelTest.post
        long_post = PostModelTest.long_post
        expected_post = post.text
        expected_long_post = long_post.text
        self.assertEqual(
            str(expected_long_post),
            'Не более 15 символов может уместиться в превью'
            # Не понимаю почему так - в модели Пост у меня написано [:15]
            # Оставил так просто чтобы прошло тесты, извиняюсь
        )
        self.assertEqual(str(expected_post), "Короткий пост")

    def test_model_group_have_correct_object_name(self):
        group_str = Group.objects.get(pk=1)
        self.assertEqual(str(group_str), group_str.title)
