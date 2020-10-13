from django.test import TestCase
from django.test import Client
from .models import User, Post, Group
from .forms import PostForm
from . import views
from django.urls import reverse


class ScriptsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
                        first_name = 'sarah',
                        last_name = 'connor',
                        username='sarah77', 
                        email='connor.s@skynet.com', 
                        password='12345'
                        )
        self.group = Group.objects.create(title='original_group', slug='original')
        # перенес пост из локальных тестов сюда,
        # чтобы устранить замечания о создании структуры данных с урлами
        self.post = Post.objects.create(text='GOGOGOGOGO', author=self.user, group=self.group)
        self.not_login_user = Client()
        self.login_user = Client()
        self.login_user.force_login(self.user)
        self.current_urls={
            'POST_EDIT': reverse(
                            'post_edit', 
                            kwargs={'username': self.user.username, 'post_id': self.post.id}
                            ),
            'GROUP_POSTS_test_edit': reverse(
                                        'group_posts', 
                                        kwargs={'slug': 'test_edit'}
                                        ),
            'GROUP_POSTS_original': reverse(
                                        'group_posts', 
                                        kwargs={'slug': 'original'}
                                        ),
            'PROFILE_username': reverse(
                                    'profile', 
                                    kwargs={'username': self.user.username}
                                    ),
            'PROFILE_text': reverse(
                                    'profile', 
                                    kwargs={'username': self.post.text}
                                    ),
            'POST': reverse(
                            'post', 
                            kwargs={'username': self.user.username, 'post_id': self.post.id}
                            ),
            'INDEX': reverse('index'),
            }


    def check_method(self, url, search):
        self.response = self.login_user.get(url)
        self.assertContains(self.response, search)


    def check_method_NOT(self, url, search):
        self.response = self.login_user.get(url)
        self.assertNotContains(self.response, search)
    
    def check(self, url, wonder_attr, search):
        self.response = self.login_user.get(url)
        self.assertEqual(str(self.response.context[wonder_attr]), search)


    def test_profile(self):
        response = self.login_user.get(self.current_urls['PROFILE_username'])
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)
    

    def test_post_autorized(self):
        response = self.login_user.post(reverse('new_post'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertEqual(response.context['year'], 2020)
        
        response = self.login_user.get(self.current_urls['PROFILE_username'])
        self.assertEqual(len(response.context['paginator'].object_list), 1)
        self.assertContains(response, self.post.text)
        self.assertEqual(response.context['author'].username, self.user.username)


    def test_post_NotAutorized(self):
        response = self.not_login_user.post(reverse('new_post'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, (
                            f'{reverse("login")}?next='
                            f'{reverse("new_post")}'
                            )
                        )
        self.assertEqual(len(response.context['paginator'].object_list), 1)
                        
                       
    def test_post_on_pages(self):
        self.check_method(self.current_urls['INDEX'], self.post.text)
        self.check_method(self.current_urls['POST'], self.post.text)
        self.check_method(self.current_urls['PROFILE_username'], self.post.text)

    
    def test_edit_post(self):
        self.group_new = Group.objects.create(title='test_group_after_edit', slug='test_edit')
        new_data = {
            'text': 'new_text_after_edit',
            'group': self.group_new.id,
            }
        response = self.login_user.post(
                            self.current_urls['POST_EDIT'],
                            new_data,
                            follow=True
                            )
        self.assertEqual(str(response.context['post']), new_data['text'])
        self.assertContains(response, new_data['group'], status_code=200)

        self.check_method_NOT(self.current_urls['GROUP_POSTS_original'], new_data['text'])

        self.check_method_NOT(self.current_urls['GROUP_POSTS_test_edit'], self.post.text)
        self.check_method_NOT(self.current_urls['GROUP_POSTS_test_edit'], self.group)
        
        self.check_method(self.current_urls['GROUP_POSTS_test_edit'], new_data["text"])
        self.check(self.current_urls['GROUP_POSTS_test_edit'], 'group', self.group_new.title)

        self.check(self.current_urls['PROFILE_username'], 'post', new_data["text"])
        self.check_method(self.current_urls['PROFILE_username'], new_data["group"])

        self.check(self.current_urls['POST'], 'post', new_data["text"])
        self.check_method(self.current_urls['POST'], new_data["group"])

        self.check_method(self.current_urls['INDEX'], new_data["text"])
        self.check_method(self.current_urls['INDEX'], new_data["group"])

        #response=self.login_user.get(self.current_urls['INDEX'])
        #print(response.context.keys())

        #def check(self, url, wonder_attr, search):
        #self.response = self.login_user.get(url)  