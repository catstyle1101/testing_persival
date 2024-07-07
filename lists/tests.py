from django.test import TestCase, RequestFactory
from django.urls import resolve
from lists.views import home_page
from lists.models import Item


class HomePageTest(TestCase):
    def test_home_page_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_can_save_a_POST_request(self):
        response = self.client.post("/", data={"item_text": "A new list item"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        response = self.client.post("/", data={"item_text": "A new list item"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/lists/the-one-list-in-the-world/")

    def test_only_saves_items_when_nessesary(self):
        """Тест: сохраняет элементы, только когда нужно."""
        self.client.get("/")
        self.assertEqual(Item.objects.count(), 0)


class ItemModelTest(TestCase):
    """Тест модели элемента списка."""

    def test_saving_and_retrieving_items(self):
        """Тест сохранения и получения элементов списка."""
        first_item = Item()
        first_item.text = "The first (ever) item"
        first_item.save()

        second_item = Item()
        second_item.text = "Item the second"
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, "The first (ever) item")
        self.assertEqual(second_saved_item.text, "Item the second")


class ListViewTest(TestCase):
    """Тест представления списка."""

    def test_uses_list_template(self):
        """Тест: используется шаблон списка."""
        response = self.client.get("/lists/the-one-list-in-the-world/")
        self.assertTemplateUsed(response, "list.html")

    def test_displays_all_items(self):
        """Тест: отображаются все элементы списка."""
        Item.objects.create(text="itemey 1")
        Item.objects.create(text="itemey 2")

        response = self.client.get("/lists/the-one-list-in-the-world/")

        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
