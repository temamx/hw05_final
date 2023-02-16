import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from posts.models import Post, User, Follow
from django.urls import reverse
from django.core.cache import cache
from posts.tests.shortcuts import group_create, post_create


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TEST_AMOUNT_POST = 5
        cls.user_author = User.objects.create_user(username='StasBasov')
        cls.user = User.objects.create_user(username='Guest')
        cls.group = group_create('Заголовок', 'Описание')
        for i in range(1, 11):
            cls.post = post_create(f'Пост {i}', cls.user_author, cls.group)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_author,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.new_user = User.objects.create_user(username='FollowUser')
        self.new_user_client = Client()
        self.new_user_client.force_login(self.new_user)
        self.new_user_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'FollowUser'}
            )
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'StasBasov'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': '1'}): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        """Проверка работы Paginator"""
        pages_names = {
            'posts:index': {},
            'posts:group_list': {'slug': 'slug'},
            'posts:profile': {'username': self.user_author.username},
        }
        for page, args in pages_names.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(
                    reverse(page, kwargs=args))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_post_appers_on_pages_with_group(self):
        """Если при создании поста указать группу,
        то пост появляется на страницах
        """
        pages_names = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'slug'}),
            reverse('posts:profile', kwargs={'username': self.user_author}),
        )
        self.post = Post.objects.create(
            text='Пост 1',
            author=self.user_author,
            group=self.group,
        )
        for page in pages_names:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                new_post = response.context['page_obj'][0]
                post_text = new_post.text
                post_group = new_post.group
                post_author = new_post.author
                self.assertEqual(post_text,
                                 'Пост 1')
                self.assertEqual(post_group, self.group)
                self.assertEqual(post_author, self.user_author)

    def test_cache_index(self):
        """Проверка хранения и очищения кэша для index."""
        response = self.author_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Пост 1',
            author=self.user_author,
        )
        response_old = self.author_client.get(reverse('posts:index'))
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = self.author_client.get(reverse('posts:index'))
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)

    def test_follow_on_authors(self):
        """Проверка, что авторизованный пользователь
        может подписываться на других пользователей
        """
        response1 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object1 = response1.context['page_obj'].object_list
        self.assertEqual((len(page_object1)), 0)

        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.post.author})
        )
        response2 = self.authorized_client.get(reverse('posts:follow_index'))
        page_object2 = response2.context['page_obj'].object_list
        self.assertEqual((len(page_object2)), 10)

    def test_unfollow_on_author(self):
        """Проверка, что авторизованный пользователь
        может удалять их из подписок других пользователей
        """
        for i in range(self.TEST_AMOUNT_POST):
            self.post = post_create(
                'test_post_№' + str(i),
                self.user,
                self.group
            )
        follow_count_before = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user.username}))
        follow_count_after = Follow.objects.count()
        self.assertEqual(follow_count_before, follow_count_after)
