from django.contrib.auth.models import User
from django.urls import reverse, resolve
from django.test import TestCase

from myvote.models import Poll, Option, Vote
from tests.testing_helpers import create_test_user, create_polls

class ExploreTests(TestCase):
    def setUp(self):
        self.url = reverse('explore polls')
        self.user = create_test_user()
        create_polls(self.user, amount=10)

    def test_create_polls(self):
        pass



class ExploreRecentTests(TestCase):
    def setUp(self):
        url = reverse('explore recent polls')
