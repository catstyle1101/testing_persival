import uuid

from django.contrib import auth
from django.db import models


auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


class User(models.Model):
    email = models.EmailField(unique=True, primary_key=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    is_anonymous = False
    is_authenticated = True


class Token(models.Model):
    email = models.EmailField()
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
