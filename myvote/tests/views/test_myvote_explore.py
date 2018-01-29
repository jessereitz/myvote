from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from myvote.models import Poll, Option, Vote
from tests.testing_helpers import create_test_user, create_polls

# CONSTANTS
POLLS_PER_PAGE = 10
USERNAME = 'testuser'
PASSWORD = 'testpassword12'

class ExploreTests(TestCase):
    def setUp(self):
        self.url = reverse('explore polls')
        self.user = create_test_user(username=USERNAME, password=PASSWORD)
        create_polls(self.user, amount=10)

    def login_helper(self):
        return self.client.login(username=USERNAME, password=PASSWORD)

    def test_logged_out_view(self):
        """
            Get request to explore view should return 200 and a list of ten
            polls.
        """
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)

    def test_logged_in_view(self):
        """
            Should return the same as test_logged_out_view.
        """
        login = self.login_helper()
        self.assertTrue(login)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)

    def test_pagination_links_and_poll_lists(self):
        """
            Tests for next/previous page links.
        """
        create_polls(self.user, start_num=10, amount=30)
        get_response = self.client.get(self.url)
        # view should still return 10 polls in get request
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)

        # Get page 1
        self.assertContains(get_response, "?page=2")
        self.assertNotContains(get_response, "?page=1")
        self.assertNotContains(get_response, "?page=3")
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)

        # page 2
        get_page_2 = self.client.get(self.url + "?page=2")
        self.assertContains(get_page_2, "?page=1")
        self.assertContains(get_page_2, "?page=3")
        self.assertNotContains(get_page_2, "?page=2")
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)

        # page 3
        get_page_3 = self.client.get(self.url + "?page=3")
        self.assertNotContains(get_page_3, "?page=1")
        self.assertContains(get_page_3, "?page=2")
        self.assertNotContains(get_page_3, "?page=3")
        self.assertEqual(len(get_response.context.get('polls')), POLLS_PER_PAGE)


class ExploreRecentTests(TestCase):
    def setUp(self):
        self.user = create_test_user(username=USERNAME, password=PASSWORD)
        # url to view self.user recent polls
        self.url = reverse('explore recent polls', kwargs={'user_id':1})

    def login_helper(self):
        return self.client.login(username=USERNAME, password=PASSWORD)

    def test_logged_out_view_less_than_10(self):
        """
            Should display the most recent polls from user.
        """
        create_polls(self.user, amount=3)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 3)

    def test_logged_out_view_exactly_10(self):
        """
            Should display the 10 most recent polls from user.
        """
        create_polls(self.user, amount=10)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 10)
        self.assertNotContains(get_response, '?page=2')

    def test_logged_out_view_more_than_10(self):
        """
            Should display the 10 most recent polls from user with pagination.
        """
        create_polls(self.user, amount=20)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 10)
        self.assertContains(get_response, '?page=2')

    def test_logged_in_view_less_than_10(self):
        """
            Should display the most recent polls from user.
        """
        login = self.login_helper()
        self.assertTrue(login)
        create_polls(self.user, amount=3)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 3)

    def test_logged_in_view_exactly_10(self):
        """
            Should display the 10 most recent polls from user.
        """
        login = self.login_helper()
        self.assertTrue(login)
        create_polls(self.user, amount=10)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 10)
        self.assertNotContains(get_response, '?page=2')

    def test_logged_in_view_more_than_10(self):
        """
            Should display the 10 most recent polls from user with pagination.
        """
        login = self.login_helper()
        self.assertTrue(login)
        create_polls(self.user, amount=20)
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.context.get('polls')), 10)
        self.assertContains(get_response, '?page=2')
