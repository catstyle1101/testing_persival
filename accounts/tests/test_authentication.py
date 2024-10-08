import uuid
from unittest.mock import patch, call, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token

User = get_user_model()


class AuthenticateTest(TestCase):
    def test_returns_None_if_no_such_token(self):
        request = self.client.get("/")
        result = PasswordlessAuthenticationBackend().authenticate(
            request, (uuid.uuid4())
        )
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        request = self.client.get("/")
        email = "edith@example.com"
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(request, token.uid)
        new_user = User.objects.get(email=email)
        self.assertEqual(new_user, user)

    def test_returns_extisting_user_with_correct_email_if_token_exists(self):
        request = self.client.get("/")
        email = "edith@example.com"
        existing_user = User.objects.get_or_create(email=email)[0]
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(request, uid=token.uid)
        self.assertEqual(existing_user, user)


class GetUserTest(TestCase):
    def test_gets_user_by_email(self):
        User.objects.create(email="another@example.com")
        desired_user = User.objects.create(email="edith@example.com")
        found_user = PasswordlessAuthenticationBackend().get_user("edith@example.com")
        self.assertEqual(found_user, desired_user)

    def test_returns_None_if_no_user_with_that_email(self):
        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user("edith@example.com")
        )
