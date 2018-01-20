from django.test.utils import setup_test_environment
from django.test import TestCase, Client
from django.urls import reverse

from myvote.views import index

class IndexViewTest(TestCase):
    def setup(self):
        setup_test_environment()
        self.client = Client()

    def test_index_view_returns_ok(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_second_test(self):
        self.assertEqual(1, 1)
