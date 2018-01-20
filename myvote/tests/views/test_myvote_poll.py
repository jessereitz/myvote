from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from myvote.views import index, create_poll, view_poll, vote_poll
from myvote.forms import PollCreationForm
from myvote.models import Poll, Option

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
        self.assertRedirects(post_response, self.login_url)

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
        self.poll = Poll(name="test_poll", owner=self.user)
        self.poll.save()
        option1 = Option(option_text="test_option_1", poll=self.poll)
        option1.save()
        option2 = Option(option_text="test_option_2", poll=self.poll)
        option2.save()
        self.option1 = option1
        self.option2 = option2
        self.vote_poll_url = reverse('vote poll', kwargs={'poll_id': self.poll.id, 'option_id': option1.id})
        self.view_poll_url = reverse('view poll', kwargs={'poll_id': self.poll.id})
        self.login_url = reverse('account:login') + "?next=" + self.vote_poll_url


    def test_not_logged_in_redirect(self):
        """ Should redirect to login page if user is not logged in. """
        response = self.client.get(self.vote_poll_url)
        self.assertRedirects(response, self.login_url)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_not_voted_redirect_to_view_poll(self):
        """
            Should redirect to view poll page if user is logged in and has
            not yet voted on the poll.
        """
        login = self.client.login(username="testuser", password="testpassword12")
        self.assertTrue(login)
        response = self.client.get(self.vote_poll_url)
        self.assertRedirects(response, self.view_poll_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(self.option1.votes.all()), 1)

    def test_logged_in_already_voted_not_vote_again(self):
        """
            After a user has already voted they should not be allowed to vote
            again.
        """
        login = self.client.login(username="testuser", password="testpassword12")
        self.assertTrue(login)
        response = self.client.get(self.vote_poll_url)
        self.assertEqual(len(self.option1.votes.all()), 1)
        response2 = self.client.get(self.vote_poll_url)
        self.assertEqual(len(self.option1.votes.all()), 1)
        self.assertEqual(len(self.option2.votes.all()), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response2.status_code, 302)

class PollDeletionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpassword12")
        self.poll = Poll(name="test_poll", owner=self.user)
        self.poll.save()
        option1 = Option(option_text="test_option_1", poll=self.poll)
        option1.save()
        option2 = Option(option_text="test_option_2", poll=self.poll)
        option2.save()
        self.option1 = option1
        self.option2 = option2
        self.delete_poll_url = reverse('delete poll', kwargs={'poll_id': self.poll.id})
        self.login_url = reverse('account:login') + "?next=" + self.delete_poll_url


    def test_not_logged_in_delete_poll_redirects(self):
        """
            Should redirect user to login page if not logged in.
        """
        get_response = self.client.get(self.delete_poll_url)
        post_response = self.client.post(self.delete_poll_url)
        self.assertEqual(get_response.status_code, 302)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(get_response, self.login_url)
        self.assertRedirects(post_response, self.login_url)

    def test_logged_in_not_owner_delete_poll_denied(self):
        """
            Should redirect to home page if logged-in user tries to delete
            another user's poll.
        """
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword12")
        login = self.client.login(username="testuser2", password="testpassword12")
        get_response = self.client.get(self.delete_poll_url)
        post_response = self.client.post(self.delete_poll_url)
        self.assertEqual(get_response.status_code, 302)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(get_response, reverse('home'))
        self.assertRedirects(post_response, reverse('home'))
        self.assertEqual(len(self.user.polls.all()), 1)

    def test_logged_in_delete_owned_poll(self):
        """
            Should display delete button on get. Should delete logged-in user's
            own poll on POST.
        """
        login = self.client.login(username="testuser", password="testpassword12")
        get_response = self.client.get(self.delete_poll_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(self.user.polls.all()), 1)

        post_response = self.client.post(self.delete_poll_url)
        self.assertEqual(post_response.status_code, 302)
        self.assertRedirects(post_response, reverse('home'))
        self.assertEqual(len(self.user.polls.all()), 0)
