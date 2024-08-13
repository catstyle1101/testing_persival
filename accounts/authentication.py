from accounts.models import Token, User
from django.contrib.auth.backends import BaseBackend


class PasswordlessAuthenticationBackend(BaseBackend):
    def authenticate(self, request, uid):
        try:
            token = Token.objects.get(uid=uid)
            return User.objects.get_or_create(email=token.email)[0]
        except Token.DoesNotExist:
            return None

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
