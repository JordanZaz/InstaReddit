from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from .models import Post
from django.urls import reverse
from . import views
from django.contrib.messages.storage.fallback import FallbackStorage
# from django.utils import timezone
# from django.contrib import messages
# from gorl.forms import PostForm


class PostListViewTestCase(TestCase):
    def setUp(self):
        # Create user and post objects
        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.post = Post.objects.create(
            title='Test Post', body='Test post content', author=self.user)

    def test_post_list_view(self):
        # Make a client request to the post list view
        client = Client()
        response = client.get('/')

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the post is in the response context
        posts = response.context['posts']
        post_exists = False
        for p in posts:
            if p.title == self.post.title and p.body == self.post.body:
                post_exists = True
                break
        self.assertTrue(post_exists)

        # Check that the template used for the response is the correct one
        self.assertTemplateUsed(response, 'gorl/post_list.html')

        # Check that the title in the context is 'Home'
        self.assertEqual(response.context['title'], 'Home')

        # Check that the default posts_per_page in the context is 5
        self.assertEqual(response.context['posts_per_page'], 5)


class SearchViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='secret')
        self.post = Post.objects.create(
            author=self.user, title='Test Post', body='Test Content')

    def test_search_view(self):
        # Create a request and pass it to the view
        request = self.factory.get(reverse('search'))
        request.user = self.user
        response = views.SearchView.as_view()(request)

        response.render()

        # Check the status code of the response
        self.assertEqual(response.status_code, 200)

        # Check if the post and comment objects are in the context data
        self.assertIn('Test Post', str(response.content))

        # Check if the title and filterset are in the context data
        self.assertIn('Search', str(response.content))

        # Check if the post count is in the context data
        self.assertIn('post_count', response.context_data)


class RegisterViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_register_view(self):
        # Create a request and pass it to the view
        request = self.factory.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        request.user = AnonymousUser()
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = views.register(request)

        # Check that the user has been created
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')

        # Check that the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

        # Check that the success message is stored in the messages framework
        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), 'Account created for testuser! You are now able to login.')


class LoginViewTestCase(TestCase):
    def setUp(self):
        # create a test user
        self.test_user = User.objects.create_user(
            username='testuser', password='password')
        # create a client for sending requests
        self.client = Client()

    def test_login_view(self):
        # send a post request to the login view with the test user's credentials
        response = self.client.post(
            '/login/', {'username': 'testuser', 'password': 'password'})
        # check that the response is a redirect to the home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_invalid_login(self):
        # send a post request to the login view with incorrect credentials
        response = self.client.post(
            '/login/', {'username': 'testuser', 'password': 'incorrect'})
        # check that the response is a success status code (200)
        self.assertEqual(response.status_code, 200)
        # check that the response contains an error message
        self.assertContains(
            response, 'Please enter a correct username and password Gorl.')


class CreatePostViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser', password='password123')

    def test_create_post_view(self):
        request = self.factory.post(reverse('post-create'), {
            'title': 'Test Post',
            'body': 'This is a test post',
            'file_url': 'https://example.com/test.pdf'
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = views.CreatePostView.as_view()(request)

        # Check that the post has been created
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'Test Post')
        self.assertEqual(Post.objects.get().body, 'This is a test post')
        self.assertEqual(Post.objects.get().file_url,
                         'https://example.com/test.pdf')
        self.assertEqual(Post.objects.get().author, self.user)

        # Check that the user is redirected to the home page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        # Check that the success message is stored in the messages framework
        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Post Created Gorl!')
