from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
# https://postimg.cc/BXJSWv7T
# Спасибо вам, что даете такую подробную инфу
# Настроил PyCharm, исправил с long post
# Прочитал про классы, вроде исправил

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
        self.post
        self.long_post
        expected_post = self.post.text
        self.assertEqual(
            str(self.long_post),
            'Не более 15 сим'
        )
        self.assertEqual(str(expected_post), "Короткий пост")

    def test_model_group_have_correct_object_name(self):
        group_str = Group.objects.get(pk=1)
        self.assertEqual(str(group_str), group_str.title)
