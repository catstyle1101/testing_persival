from django.test import TestCase
from django.utils.html import escape

from lists.forms import ItemForm
from lists.models import List, Item


class HomePageTest(TestCase):
    def test_home_page_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    """Тест представления списка."""

    def test_uses_list_template(self):
        """Тест: используется шаблон списка."""
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_passes_correct_list_to_template(self):
        """Тест: передается правильный шаблон списка."""
        _ = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertEqual(response.context["list"], correct_list)

    def test_displays_only_items_for_that_list(self):
        """Тест: отображаются все элементы списка."""
        correct_list = List.objects.create()
        Item.objects.create(text="itemey 1", list=correct_list)
        Item.objects.create(text="itemey 2", list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text="another list itemey 1", list=other_list)
        Item.objects.create(text="another list itemey 2", list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")

        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
        self.assertNotContains(response, "another list itemey 1")
        self.assertNotContains(response, "another list itemey 2")

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """Тест: можно сохранить post запрос в существующий список."""
        _ = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/",
            data={"item_text": "A new item for the existing list"},
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(Item.objects.first().text, "A new item for the existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        """Тест: переадресуется в представление списка."""
        _ = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f"/lists/{correct_list.id}/",
            data={"item_text": "A new item for the existing list"},
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post(
            f"/lists/{list_.id}/",
            data={"item_text": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)


class NewListTest(TestCase):
    """Тест нового списка."""

    def test_can_save_a_POST_request(self):
        """Тест: можно сохранить POST запрос."""
        self.client.post("/lists/new", data={"item_text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        response = self.client.post("/lists/new", data={"item_text": "A new list item"})
        new_list = List.objects.first()
        self.assertRedirects(response, f"/lists/{new_list.id}/")

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post("/lists/new", data={"item_text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        self.client.post("/lists/new", data={"item_text": ""})
        self.assertEqual(Item.objects.count(), 0)
        self.assertEqual(List.objects.count(), 0)
