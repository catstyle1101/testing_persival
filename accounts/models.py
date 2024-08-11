import uuid

from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = True


class Token(models.Model):
    email = models.EmailField()
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
