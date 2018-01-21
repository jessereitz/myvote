from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from accounts.views import signup
from accounts.forms import SignUpForm, ChangePasswordForm, ChangeEmailForm, DeleteAccountForm

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
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user.check_password('newtestpassword12'))
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


class ChangeEmailTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword12"
        self.email = "test@example.com"
        self.user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.change_email_url = reverse('account:change email')
        self.login_url = reverse('account:login') + "?next=/account/change_email/"

    def login(self):
        """
            Reusable method to log in user created in the setUp method.
        """
        login = self.client.login(username=self.username, password=self.password)
        return login

    def get_change_email(self):
        """
            Reusable method to send get request to self.change_email_url.
        """
        return self.client.get(self.change_email_url)

    def post_change_email(self, data=None):
        """
            Reusable method to send post request to self.change_email_url.
        """
        return self.client.post(self.change_email_url, data)

    def test_user_not_logged_in_redirects_from_change_email(self):
        """
            Should redirect user to login page if they aren't logged in.
        """
        get_response = self.get_change_email()
        post_response = self.post_change_email()
        self.assertRedirects(get_response, self.login_url)
        self.assertRedirects(post_response, self.login_url)

    def test_user_logged_in_get_displays_change_email_form(self):
        """
            Should display a change email form if user is logged in.
        """
        self.assertTrue(self.login())
        get_response = self.get_change_email()
        self.assertEqual(get_response.status_code, 200)
        form = get_response.context.get('form')
        self.assertIsInstance(form, ChangeEmailForm)

    def test_user_logged_in_post_changes_email(self):
        """
            Should successfully change a user's email if new email matches
            confirmation and is an actual email.
        """
        form_data = {
            'password': self.password,
            'new_email': "new@email.com",
            'new_email2': "new@email.com"
        }
        self.assertTrue(self.login())
        post_response = self.post_change_email(form_data)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('account:overview'))
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.email, 'new@email.com')

    def test_user_logged_in_new_emails_dont_match(self):
        """
            Should redisplay ChangeEmailForm if new_email and new_email2 don't
            match. User's email should NOT be changed.
        """
        form_data = {
            'password': self.password,
            'new_email': 'new@email.com',
            'new_email2': 'wrong@email.com'
        }
        self.assertTrue(self.login())
        post_response = self.post_change_email(form_data)
        self.assertEqual(post_response.status_code, 200)
        form = post_response.context.get('form')
        self.assertIsInstance(form, ChangeEmailForm)
        self.assertContains(post_response, 'New emails must match')
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.email, self.email)
        self.assertNotEqual(user.email, 'new@email.com')
        self.assertNotEqual(user.email, 'wrong@email.com')

    def test_user_logged_in_change_email_password_invalid(self):
        """
            Should redisplay ChangeEmail form if given password is incorrect.
            Should NOT change email.
        """
        form_data = {
            'password': 'wrongpassword12',
            'new_email': "new@email.com",
            'new_email2': "new@email.com"
        }
        self.assertTrue(self.login())
        post_response = self.post_change_email(form_data)
        self.assertEqual(post_response.status_code, 200)
        form = post_response.context.get('form')
        self.assertIsInstance(form, ChangeEmailForm)
        self.assertContains(post_response, 'Incorrect password')
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.email, self.email)
        self.assertNotEqual(user.email, 'new@email.com')


class DeleteAccountTests(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword12"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.delete_account_url = reverse('account:delete account')
        self.login_url = reverse('account:login') + "?next=/account/delete_account/"

    def login(self):
        """
            Reusable method to log in user created in the setUp method.
        """
        login = self.client.login(username=self.username, password=self.password)
        return login

    def get_delete_account(self):
        """
            Reusable method to send get request to self.delete_account_url.
        """
        return self.client.get(self.delete_account_url)

    def post_delete_account(self, data=None):
        """
            Reusable method to send post request to self.change_email_url.
        """
        return self.client.post(self.delete_account_url, data)


    def test_user_not_logged_in_redirects_from_delete_account(self):
        """
            Should redirect user to login page if they aren't logged in.
        """
        get_response = self.get_delete_account()
        post_response = self.post_delete_account()
        self.assertRedirects(get_response, self.login_url)
        self.assertRedirects(post_response, self.login_url)

    def test_user_logged_in_get_displays_delete_account_form(self):
        """
            Should display the DeleteAccountForm if user is logged in.
        """
        self.assertTrue(self.login())
        get_response = self.get_delete_account()
        self.assertEqual(get_resposne.status_code, 200)
        form = get_response.context.get('form')
        self.assertIsInstance(form, DeleteAccountForm)

    def test_user_logged_in_post_deletes_account(self):
        """
            Should delete user's account if user is logged in and provided
            information is valid.
        """
        form_data = {
            'password': self.password,
            'password2': self.password
        }
        post_response = self.post_delete_account(form_data)
        self.assertRedirects(post_response, reverse('home'))
        user = User.object.get(pk=self.user.id)
        self.assertFalse(user)

    def test_user_logged_in_invalid_passwords_dont_delete_account(self):
        """
            Should redisplay DeleteAccountForm if user provides invalid passwords.
            Should NOT delete user's account
        """
        wrong_password1 = {
            'password': 'wrongpassword',
            'password2': self.password,
        }
        wrong_password2 = {
            'password': self.password,
            'password2': 'wrongpassword'
        }
        wrong_password_both = {
            'password': 'wrongpassword',
            'password2': 'wrongpassword'
        }
        wrong_password_both_different = {
            'password': 'wrongpassword',
            'password2': 'differentwrongpassword'
        }
        self.assertTrue(self.login())
        post_response_1 = self.post_delete_account(wrong_password1)
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user)
        post_response_2 = self.post_delete_account(wrong_password2)
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user)
        post_response_3 = self.post_delete_account(wrong_password_both)
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user)
        post_response_4 = self.post_delete_account(wrong_password_both_different)
        user = User.objects.get(pk=self.user.id)
        self.assertTrue(user)
        self.assertEqual(post_response_1.status_code, 200)
        self.assertEqual(post_response_2.status_code, 200)
        self.assertEqual(post_response_3.status_code, 200)
        self.assertEqual(post_response_4.status_code, 200)
        form_1 = post_response_1.context.get('form')
        form_2 = post_response_2.context.get('form')
        form_3 = post_response_3.context.get('form')
        form_4 = post_response_4.context.get('form')
        self.assertIsInstance(form_1, DeleteAccountForm)
        self.assertIsInstance(form_2, DeleteAccountForm)
        self.assertIsInstance(form_3, DeleteAccountForm)
        self.assertIsInstance(form_4, DeleteAccountForm)
