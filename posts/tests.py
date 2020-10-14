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
        self.not_login_user = Client()
        self.login_user = Client()
        self.login_user.force_login(self.user)

  
    def check(self, url, text, author, group):
        response = self.login_user.get(url)
        self.assertEqual(str(response.context['post']), text)
        self.assertEqual(str(response.context['author']), author)
        self.assertContains(response, group)


    def test_profile(self):
        url=reverse(
                    'profile', 
                    kwargs={'username': self.user.username}
                    )
        response = self.login_user.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(response.context['author'].username, self.user.username)
    

    def test_post_autorized(self):
        response = self.login_user.post(
                                   reverse('new_post'),
                                   {'text': 'test_text', 'group': self.group.id},
                                   follow=True
                                   )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, 'test_text')
        self.assertContains(response, self.group.id)


    def test_post_NotAutorized(self):
        urls = [reverse("new_post"), reverse("index"), reverse("login")]
        response = self.not_login_user.post(reverse("new_post"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, (
                            f'{urls[2]}?next='
                            f'{urls[0]}'
                            )
                        )
        response = self.not_login_user.get(urls[1])
        self.assertEqual(len(response.context['paginator'].object_list), 0)
                        
                       
    def test_post_on_pages(self):
        post = Post.objects.create(text='GOGOGOGOGO', author=self.user, group=self.group)
        urls = [
            reverse("index"),
            reverse("post", kwargs={"username": self.user.username, "post_id": post.id}),
            reverse("profile", kwargs={"username": self.user.username})
        ]
        response = self.login_user.post(urls[0])
        self.assertIn(post.text, str(response.context['paginator'].object_list))
        self.check(urls[1], post.text, self.user.username, self.group.id)
        self.check(urls[2], post.text, self.user.username, self.group.id)


    def test_edit_post(self):
        post = Post.objects.create(text='GOGOGOGOGO', author=self.user, group=self.group)
        group_new = Group.objects.create(title='test_group_after_edit', slug='test_edit')
        urls = [
            reverse("post_edit", kwargs={"username": self.user.username, "post_id": post.id}),
            reverse("group_posts", kwargs={"slug": "test_edit"}),
            reverse("profile", kwargs={"username": self.user.username}),
            reverse("post", kwargs={"username": self.user.username, "post_id": post.id}),
            reverse("index"),
            reverse("group_posts", kwargs={"slug": "original"})
        ]
        new_data = {
            'text': 'new_text_after_edit',
            'group': group_new.id,
            }
        response = self.login_user.post(
                            urls[0],
                            new_data,
                            follow=True
                            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['post']), new_data['text'])
        self.assertContains(response, new_data['group'], status_code=200)

        response = self.login_user.post(urls[1])
        self.assertIn(new_data['text'], str(response.context['paginator'].object_list))
        self.assertEqual(group_new.title, str(response.context['group']))

        response = self.login_user.post(urls[2])
        self.assertIn(new_data['text'], str(response.context['paginator'].object_list))
        self.assertEqual(self.user.username, str(response.context['author']))

        response = self.login_user.post(urls[3])
        self.assertIn(new_data['text'], str(response.context['post']))
        self.assertEqual(self.user.username, str(response.context['author']))

        response=self.login_user.get(urls[4])
        print(response.context)
        self.assertIn(new_data['text'], str(response.context['paginator'].object_list))
        self.assertEqual(self.user.username, str(response.context['user']))

        response = self.login_user.post(urls[5])
        self.assertNotIn(new_data['text'], str(response.context['paginator'].object_list))
        self.assertNotEqual(group_new.title, str(response.context['group']))