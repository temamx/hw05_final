from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from posts.forms import PostForm
from posts.models import Post, Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import tempfile
from django.core.cache import cache
from yatube.posts.tests.shortcuts import group_create
from yatube.posts.views import post_create

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='reader')
        cls.group = group_create('Группа', 'Описание')
        cls.post = post_create('Пост', cls.user, cls.group)
        cls.form = PostForm

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_create_post(self):
        """Проверка создаётся ли новая запись в базе данных"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'NoNameUser'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertTrue(Post.objects.filter(
            text='Пост',
            group=self.group.id,
            image=post.image,
        ).exists())

    def test_edit_post(self):
        """Происходит изменение поста с post_id в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый текст поста',
            'author': self.author,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id, )),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     args=(self.post.id, )))
        edit_post = Post.objects.all().last()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, 'Изменённый текст поста',)
        self.assertEqual(edit_post.author, self.author)

    def test_comment_posts_only_authorized_client(self):
        """Проверяем, что комментировать посты может
        только авторизованный пользователь
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/',
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_comment(self):
        """Проверяем, что после успешной отправки
        комментарий появляется на странице поста
        """
        form_data = {
            'author': self.author,
            'text': 'Текст комментария',
        }
        response = self.authorized_client.get(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_following_posts_author(self):
        """Проверка отображения новой записи автора в Ленте подписок"""
        cache.clear()
        following_posts = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group,
            'author': self.author,
            'image': uploaded
        }
        response = self.authorized_client.get(
            reverse('posts:follow_index'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), following_posts)
