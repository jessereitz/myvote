from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from myvote.views import index, create_poll, view_poll, vote_poll
from myvote.forms import PollCreationForm
from myvote.models import Poll

class PollCreationTests(TestCase):
    def setUp(self):
        """ Creates a user. Returns get response for poll creation url. """
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword12")
        self.create_poll_url = reverse('create poll')
        self.home_url = reverse('home')
        self.login_url = reverse('account:login') + "?next=/create_poll/"

    def test_redirect_if_not_logged_in(self):
        """ Should redirect to login url if user is not logged in. Redirects
        with GET and POST methods """
        get_response = self.client.get(self.create_poll_url)
        post_response = self.client.post(self.create_poll_url)
        self.assertRedirects(get_response, self.login_url)

    def test_response_contains_poll_creation_form_if_logged_in(self):
        """ Should return a view with an instance of PollCreationForm if user is logged in."""
        login = self.client.login(username="testuser", password="testpassword12")
        response = self.client.get(self.create_poll_url)
        form = response.context.get('form')  # grab the form from response object
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(form, PollCreationForm)

    def test_poll_creation_with_good_data_for_form(self):
        """
            Should create a new poll with given options and redirect (status
            code 302).
        """
        login = self.client.login(username="testuser", password="testpassword12")
        poll_data = {
            'name': 'test poll',
            'option1': 'test_option_1',
            'option2': 'test_option_2'
        }
        post_response = self.client.post(self.create_poll_url, poll_data)
        new_poll = Poll.objects.get(name="test poll")
        new_poll_options = new_poll.options.all()

        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(new_poll != None)
        self.assertTrue(new_poll.name == 'test poll')
        self.assertTrue(new_poll_options[0].option_text, 'test_option_1')
        self.assertTrue(new_poll_options[1].option_text, 'test_option_1')

    def test_poll_not_created_with_empty_form(self):
        """
            Should NOT create a new poll if posted form is empty.
        """
        login = self.client.login(username="testuser", password="testpassword12")
        poll_data = {}
        post_response = self.client.post(self.create_poll_url, poll_data)
        all_polls = Poll.objects.all()

        self.assertTrue(len(all_polls) == 0)


class PollVotingTests(TestCase):
    def setUp(self):
        """ Creates a test user and a test poll. """
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword12")
        pass
