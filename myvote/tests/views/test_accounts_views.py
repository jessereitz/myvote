from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from accounts.views import signup
from accounts.forms import SignUpForm, ChangePasswordForm

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


class ChangePasswordTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword12"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.change_password_url = reverse('account:change password')
        self.login_url = reverse('account:login') + "?next=/account/change_password/"

    def test_user_not_logged_in_redirects_from_change_password(self):
        """
            Should redirect user to login page if they aren't logged in.
        """
        get_response = self.client.get(self.change_password_url)
        post_response = self.client.post(self.change_password_url, {})
        self.assertRedirects(get_response, self.login_url)
        self.assertRedirects(post_response, self.login_url)


    def test_user_logged_in_get_displays_change_password_form(self):
        """
            Should display a change password form if user is logged in.
        """
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        response = self.client.get(self.change_password_url)
        form = response.context.get('form')
        self.assertTrue(response.status_code, 200)
        self.assertContains(response, "Change Your Password")
        self.assertIsInstance(form, ChangePasswordForm)

    def test_user_logged_in_post_changes_password(self):
        """
            Should successfully change user's password.
        """
        form_data = {
            "old_password": self.password,
            "new_password": "newtestpassword12",
            "new_password2": "newtestpassword12"
        }
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        post_response = self.client.post(self.change_password_url, form_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('account:overview'), target_status_code=302)
        logout = self.client.logout()
        login = self.client.login(username=self.username, password="newtestpassword12")
        self.assertTrue(login)

    def test_user_logged_in_not_matching_passwords_redisplays_form(self):
        """
            Should re-display ChangePasswordForm if user inputs correct password
            but new passwords don't match. Should not change user's password.
        """
        form_data = {
            "old_password": self.password,
            "new_password": "newtestpassword12",
            "new_password2": "wrongpassword12"
        }
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        post_response = self.client.post(self.change_password_url, form_data)
        form = post_response.context.get('form')
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Change Your Password")
        self.assertContains(post_response, "New passwords must match.")
        self.assertIsInstance(form, ChangePasswordForm)
        self.client.logout()
        re_login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(re_login)

    def test_user_logged_in_incorrect_old_password_redisplays_form(self):
        """
            Should re-display ChangePasswordForm if user inputs correct old
            password. Should not change user's password.
        """
        form_data = {
            "old_password": "wrongpassword12",
            "new_password": "newtestpassword12",
            "new_password2": "newtestpassword12"
        }
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        post_response = self.client.post(self.change_password_url, form_data)
        form = post_response.context.get('form')
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Change Your Password")
        self.assertContains(post_response, "Incorrect old password")
        self.assertIsInstance(form, ChangePasswordForm)
        self.client.logout()
        re_login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(re_login)

    def test_user_logged_in_new_passwords_match_but_too_short(self):
        """
            Should re-display ChangePasswordForm if user correctly inputs old
            password and new passwords match but don't match django's password
            requirements.
        """
        form_data = {
            "old_password": self.password,
            "new_password": "pw",
            "new_password2": "pw"
        }
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        post_response = self.client.post(self.change_password_url, form_data)
        form = post_response.context.get('form')
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Change Your Password")
        self.assertIsInstance(form, ChangePasswordForm)
        self.client.logout()
        re_login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(re_login)

    def test_user_logged_in_new_passwords_match_but_no_number(self):
        """
            Should re-display ChangePasswordForm if user correctly inputs old
            password and new passwords match but don't match django's password
            requirements.
        """
        form_data = {
            "old_password": self.password,
            "new_password": "testpassword",
            "new_password2": "testpassword"
        }
        login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login)
        post_response = self.client.post(self.change_password_url, form_data)
        form = post_response.context.get('form')
        self.assertEqual(post_response.status_code, 200)
        self.assertContains(post_response, "Change Your Password")
        self.assertIsInstance(form, ChangePasswordForm)
        self.client.logout()
        re_login = self.client.login(username=self.username, password=self.password)
        self.assertTrue(re_login)
