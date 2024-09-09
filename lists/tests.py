from django.test import TestCase, RequestFactory
from django.urls import resolve
from lists.views import home_page


class HomePageTest(TestCase):
    def test_root_url_resolves_to_home_page_view(self):
        found = resolve("/")
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        request = RequestFactory()
        response = home_page(request)
        html = response.content.decode('utf-8')
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertIn("<title>To-Do lists</title>", html)
        self.assertTrue(html.endswith('</html>'))
