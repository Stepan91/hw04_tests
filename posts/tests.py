from django.test import TestCase
from django.test import Client
from .models import User, Post, Group
from .forms import PostForm
from . import views
from django.urls import reverse


class ScriptsTest(TestCase):
    urls = {
        'INDEX': reverse('index'),
        'LOGIN': reverse('login'),
        'NEW_POST': reverse('new_post'),
        }


    def setUp(self):
        self.user = User.objects.create_user(
                        first_name = 'sarah',
                        last_name = 'connor',
                        username='sarah77', 
                        email='connor.s@skynet.com', 
                        password='12345'
                        )
        self.group = Group.objects.create(title='original_group', slug='original')
        self.not_login_user = Client()
        self.login_user = Client()
        self.login_user.force_login(self.user)
    

    def check_method(self, function, search, kwargs = None):
        self.response_url = self.login_user.get(
                                reverse(
                                function,
                                kwargs=kwargs    
                                )
                            )
        self.assertContains(self.response_url, search)


    def check_method_NOT(self, function, search, kwargs = None):
        self.response_url = self.login_user.get(
                                reverse(
                                function,
                                kwargs=kwargs    
                                )
                            )
        self.assertNotContains(self.response_url, search)


    def test_profile(self):
        response = self.login_user.get(
                                reverse(
                                    'profile', 
                                    kwargs = {'username': self.user.username}
                                    )
                                )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)
    

    def test_post_autorized(self):
        response = self.login_user.post(self.urls['NEW_POST'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertEqual(response.context['year'], 2020)
        
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)
        response = self.login_user.get(reverse(
                                   'profile', 
                                   kwargs={'username': self.user.username}
                                   )
                                )
        self.assertEqual(len(response.context['paginator'].object_list), 1)
        self.assertContains(response, self.post.text)
        self.assertEqual(response.context['author'].username, self.user.username)


    def test_post_NotAutorized(self):
        response = self.not_login_user.get('/new/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, (
                            f'{self.urls["LOGIN"]}?next='
                            f'{self.urls["NEW_POST"]}'
                            )
                        )


    def test_post_on_pages(self):
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)
        self.check_method('index', self.post.text)
        self.check_method('post', self.post.text, {'username': self.user.username, 'post_id': self.post.id})
        self.check_method('profile', self.post.text, {'username': self.user.username})

    
    def test_edit_post(self):
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user)
        self.group_new = Group.objects.create(title='test_group_after_edit', slug='test_edit')
        new_data = {
            'text': 'new_text_after_edit',
            'group': self.group_new.id,
            }
        response = self.login_user.post(
                                reverse(
                                'post_edit', 
                                kwargs={'username': self.user.username, 'post_id': self.post.id}
                                ),
                            new_data,
                            follow=True
                            )
        self.assertContains(response, new_data['text'], status_code=200)
        self.assertContains(response, new_data['group'], status_code=200)

        self.check_method_NOT('group_posts', new_data['text'], {'slug': 'original'})

        self.check_method_NOT('group_posts', self.post.text, {'slug': 'test_edit'})
        self.check_method_NOT('group_posts', self.group, {'slug': 'test_edit'})
        self.check_method('group_posts', new_data["text"], {'slug': 'test_edit'})
        self.check_method('group_posts', new_data["group"], {'slug': 'test_edit'})

        self.check_method('profile', new_data["text"], {'username': self.user.username})
        self.check_method('profile', new_data["group"], {'username': self.user.username})

        self.check_method('post', new_data["text"], {'username': self.user.username, 'post_id': self.post.id})
        self.check_method('post', new_data["group"], {'username': self.user.username, 'post_id': self.post.id})

        self.check_method('index', new_data["text"])
        self.check_method('index', new_data["group"])        