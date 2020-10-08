from django.test import TestCase
from django.test import Client
from .models import User, Post, Group
from . import views
from django.urls import reverse


class ScriptsTest(TestCase):
    urls = {
        'INDEX': reverse('index'),
        'LOGIN': reverse('login'),
        'NEW_POST': reverse('new_post'),
        }
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
                        first_name = 'sarah',
                        last_name = 'connor',
                        username='sarah77', 
                        email='connor.s@skynet.com', 
                        password='12345'
                        )
        self.group = Group.objects.create(title='test_group', slug='test')
        self.urls['REDIRECT'] = (f'{self.urls["LOGIN"]}?next='
                                 f'{self.urls["NEW_POST"]}')
        self.urls['PROFILE'] = reverse(
                                   'profile', 
                                   kwargs={'username': 'sarah77'}
                                )


    # redirect_URL = reverse('profile', kwargs={'username': 'sarah77'})
 

    def test_profile(self):
        response = self.client.get('/sarah77/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)
    

    def test_post_autorized(self):
        self.client.force_login(self.user)
        response = self.client.get(self.urls['NEW_POST'])
        self.assertEqual(response.status_code, 200)


    def test_post_NotAutorized(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, self.urls['REDIRECT'])


    def test_post_on_pages(self):
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)
        
        response = self.client.get('/')
        self.assertContains(response, self.post.text, status_code=200) 

        response = self.client.post(
                       reverse(
                           'post', 
                           kwargs={
                               'username': 'sarah77', 'post_id': self.post.id
                            }
                        )
                    )
        self.assertContains(response, self.post.text, status_code=200)
    
        response = self.client.post(self.urls['PROFILE'])
        self.assertContains(response, self.post.text, status_code=200)
    
    def test_edit_post(self):
        self.client.force_login(self.user)
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)
        new_data = {
            'text': 'new_text_for_post',
            'group': self.group.id
            }
        response = self.client.post(
                        reverse(
                        'post_edit', 
                        kwargs={'username': self.user.username, 'post_id': self.post.id}
                        ),
                        new_data,
                        follow=True
                    )
        self.assertContains(response, new_data['text'], status_code=200)
        self.assertTrue(self.test_post_on_pages)
