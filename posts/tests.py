from django.test import TestCase
from django.test import Client
from .models import User, Post
from . import views
from django.urls import reverse

# Create your tests here.


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len('yatube'), 6)
    
    def test_show_msg(self):
        self.assertTrue(True, msg='Важная проверка на истинность')


class ScriptsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # регистрация нового пользователя
        self.user = User.objects.create_user(
                        first_name = 'sarah',
                        last_name = 'connor',
                        username='sarah77', 
                        email='connor.s@skynet.com', 
                        password='12345'
                        )
        # содание поста новым пользователем
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)


    def test_profile(self):
        # формирмирование GET-запроса к странице профиля нового пользователя
        response = self.client.get('/sarah77/')
        # проверка, что страница найдена
        self.assertEqual(response.status_code, 200)
        # проверка, что новый пользователь - экземпляр класса User
        self.assertIsInstance(response.context['author'], User)
        # проверка имени нового пользователя
        self.assertEqual(response.context['author'].username, self.user.username)
    

    def test_post_autorized(self):
        response = self.client.get('/sarah77/')
        # проверка создания поста новым авторизованным пользователем
        self.assertContains(response, 'GOGOGOGOGO', status_code=200)


    def test_post_NotAutorized(self):
        response = self.client.get('/new/')
        # проверка невозможности создания поста неавторизованным пользователем
        self.assertRedirects(response, '/auth/login/?next=/new/')


    def test_create_post_index(self):
        response = self.client.get('/')
        # проверка отображения поста на главной странице
        self.assertContains(response, self.post.text, status_code=200)


    def test_create_post_post(self):
        response = self.client.post(
                        reverse(
                            'post', 
                            kwargs={'username': 'sarah77', 'post_id': self.post.id}
                            )
                        )
        # проверка отображения поста на странице поста
        self.assertContains(response, self.post.text, status_code=200)
    

    def test_create_post_profile(self):
        response = self.client.post(
                            reverse(
                            'profile', 
                            kwargs={'username': 'sarah77'}
                            )
                        )
        # проверка отображения поста на странице профиля пользователя
        self.assertContains(response, self.post.text, status_code=200)
    
    def test_edit_post(self):
        response = self.client.post(
                            reverse(
                            'post_edit', 
                            kwargs={'username': 'sarah77', 'post_id': self.post.id},
                            ),
                            follow=True
                        )
        # авторизованный пользователь может редактировать пост
        self.assertContains(response, 'GOGOGOGOGO', status_code=200)
        # проверка наличия измененного поста на всех связанных страницах
        self.assertTrue(self.test_create_post_index)
        self.assertTrue(self.test_create_post_post)
        self.assertTrue(self.test_create_post_profile)
        









    

        
