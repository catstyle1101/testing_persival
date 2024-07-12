from django.db import models
from django.urls import reverse


class List(models.Model):
    """Модель списка."""

    def get_absolute_url(self):
        return reverse("view_list", kwargs={"list_id": self.id})


class Item(models.Model):
    """Элемент списка."""
    text = models.TextField(default="")
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)
