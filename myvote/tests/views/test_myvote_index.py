from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from myvote.models import Poll

class IndexViewUserWithOwnedPolls(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword12"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.poll1 = Poll(owner=self.user, name="Test Poll 1")
        self.poll2 = Poll(owner=self.user, name="Test Poll 2")
        self.poll1.save()
        self.poll2.save()
        self.home_url = reverse('home')
        self.poll1_url = reverse('view poll', kwargs={'poll_id': self.poll1.id})
        self.poll2_url = reverse('view poll', kwargs={'poll_id': self.poll2.id})


    def test_user_not_logged_in_displays_standard_homepage(self):
        """
            Should display the standard home page without any polls listed.
        """
        signup_url = reverse('account:signup')
        logout_url = reverse('account:logout')
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, signup_url)
        self.assertFalse(logout_url in response)
