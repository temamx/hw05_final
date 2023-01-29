from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group, User
from http import HTTPStatus


User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='NoNameUser')
        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Пост',
            group=cls.group,
        )

        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Пост 2',
            group=cls.group,
        )

        cls.templates = [
            '/',
            f'/group/{cls.group.slug}',
            f'/profile/{cls.user_author}',
            f'/posts/{cls.post.id}'
        ]

        cls.templates_address = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user_author.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(
            PostURLTest.user_author
        )

    def test_url_exist_for_all_users(self):
        """Доступ всех страниц любому пользователю"""
        for address in self.templates:
            with self.subTest(address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_create_for_authorized_user(self):
        """Страница /create доступна аторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_post_edit_for_author(self):
        """Страница /posts/post_id_edit доступна только автору"""
        response = self.authorized_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_create_for_anonymous_user(self):
        """Страница /create перенаправить не
        авторизованного пользователя на страницу логина
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_users_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        for address, template in self.templates_address.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_not_available_url(self):
        """Несуществующая страница выдаст ошибку"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
