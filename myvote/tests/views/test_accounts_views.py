from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from accounts.views import signup
from accounts.forms import SignUpForm

class SignupTests(TestCase):
    def setUp(self):
        url = reverse('account:signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/account/signup/')
        self.assertEqual(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)



class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('account:signup')
        data = {
            'username': 'john',
            'email': 'john@does.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirection(self):
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('account:signup')
        self.response = self.client.post(url, {})

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())

class AccountOverviewTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword12"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.account_overview_url = reverse('account:overview')
        self.login_url = reverse('account:login') + "?next=/account/"


    def test_redirect_if_not_logged_in(self):
        """
            Should redirect anonymous user to login page.
        """
        response = self.client.get(self.account_overview_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_displays_account_overview_if_logged_in(self):
        """
            Should display page with account details and links to change them.
            Editable account details are: password, email address
        """
        # TODO: Write the view!
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        response = self.client.get(self.account_overview_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)
        self.assertContains(response, reverse('account:change password'))
        self.assertContains(response, reverse('account:change email'))
        self.assertContains(response, reverse('account:delete account'))
