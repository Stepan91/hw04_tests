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
        paginator = response.context.get('paginator')
        if paginator is not None:
            self.assertEqual(response.context['paginator'].count, 1)
            post_on_page = response.context['page'][0]
        else:
            post_on_page = response.context['post']
        self.assertEqual(post_on_page.text, text)
        # если не приводить к строке - все тесты рушатся
        self.assertEqual(str(post_on_page.author), author)
        self.assertEqual(str(post_on_page.group), str(group))


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
        post = self.login_user.post( 
                                reverse('new_post'), 
                                {'text': 'test_text', 'group': self.group.id}, 
                                follow=True 
                                )
        self.check(reverse('index'), 'test_text', self.user.username, self.group)


    def test_post_NotAutorized(self):
        urls = [reverse("new_post"), reverse("index"), reverse("login")]
        try_post = self.not_login_user.post(reverse("new_post"))
        self.assertEqual(try_post.status_code, 302)
        self.assertRedirects(try_post, (
                            f'{urls[2]}?next='
                            f'{urls[0]}'
                            )
                        )
        self.assertTrue(try_post.context == None)
                        
                       
    def test_post_on_pages(self):
        post = Post.objects.create(text='GOGOGOGOGO', author=self.user, group=self.group)
        urls = [
            reverse("index"),
            reverse("post", kwargs={"username": self.user.username, "post_id": post.id}),
            reverse("profile", kwargs={"username": self.user.username})
        ]
        for i in urls:
            self.check(i, post.text, self.user.username, self.group)


    def test_edit_post(self):
        post = Post.objects.create(text='GOGOGOGOGO', author=self.user, group=self.group)
        group_new = Group.objects.create(title='test_group_after_edit', slug='test_edit')
        urls = [
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
        response = self.login_user.post(reverse('post_edit', 
                            kwargs={
                                "username": self.user.username, 
                                "post_id": post.id
                                }
                            ),
                            new_data,
                            follow=True
                            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['post']), new_data['text'])
        self.assertContains(response, new_data['group'], status_code=200)

        self.check(urls[0], new_data['text'], self.user.username, group_new)

        self.check(urls[1], new_data['text'], self.user.username, group_new.title)

        self.check(urls[2], new_data['text'], self.user.username, group_new.title)

        self.check(urls[3], new_data['text'], self.user.username, group_new.title)

        response = self.login_user.post(urls[4])
        # почему пагинатор пуст, если мы создали пост 
        # в старой группе в начале этого теста?
        self.assertEqual(len(response.context['paginator'].object_list), 0)
