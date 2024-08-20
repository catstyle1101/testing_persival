from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape

from lists.forms import ItemForm, EMPTY_ITEM_ERROR, ExistingListItemForm
from lists.models import List, Item
from lists.views import new_list

User = get_user_model()


class HomePageTest(TestCase):
    def test_home_page_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


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
            data={"text": "A new item for the existing list"},
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
            data={"text": "A new item for the existing list"},
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(
            f"/lists/{list_.id}/",
            data={"text": ""},
        )

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(text="textey", list=list1)
        response = self.client.post(
            f"/lists/{list1.id}/",
            data={"text": "textey"},
        )
        expected_error = escape("You've already got this in your list")
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.count(), 1)

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text"')


class NewListIntegratedTest(TestCase):
    """Тест нового списка."""

    def test_can_save_a_POST_request(self):
        """Тест: можно сохранить POST запрос."""
        self.client.post("/lists/new/", data={"text": "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post("/lists/new/", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        self.client.post("/lists/new/", data={"text": "new item"})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


class MyListTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertTemplateUsed(response, "my_lists.html")

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertEqual(response.context["owner"], correct_user)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        self.client.post("/lists/new/", data={"text": "new item"})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)


@patch("lists.views.NewListForm")
@patch("lists.views.redirect")
class NewListUnitTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST["text"] = "new list item"
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mock_redirect, mockNewListForm):
        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_is_valid(
        self, mock_redirect, mockNewListForm
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    def test_redirects_to_form_returned_object_if_form_valid(
        self,
        mock_redirect,
        mockNewListForm,
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch("lists.views.render")
    def test_renders_home_template_with_form_if_form_is_invalid(
        self,
        mock_render,
        mock_redirect,
        mockNewListForm,
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, mock_render.return_value)

        mock_render.assert_called_once_with(
            self.request, "home.html", {"form": mock_form}
        )

    def test_does_not_save_if_form_is_invalid(
        self,
        mock_redirect,
        mockNewListForm,
    ):
        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)


class ShareListTest(TestCase):
    def test_post_redirects_to_lists_page(self):
        owner = User.objects.create(email="a@b.com")
        self.client.force_login(owner)
        list_ = List.objects.create(owner=owner)

        response = self.client.post(
            f"/lists/{list_.pk}/share/",
            data={"sharee": "b@b.com"},
            follow=True,
        )

        self.assertRedirects(response, f"/lists/{list_.pk}/")

    def test_list_can_be_shared_with_existing_user(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        another_user = User.objects.create(email="b@b.com")
        list_ = List.objects.create(owner=user)

        self.client.post(
            f"/lists/{list_.pk}/share/",
            data={"sharee": "b@b.com"},
            follow=True,
        )

        self.assertIn(another_user, list_.shared_with.all())

    def test_share_list_creates_user_if_not_exist(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        list_ = List.objects.create(owner=user)

        self.client.post(
            f"/lists/{list_.pk}/share/",
            data={"sharee": "b@b.com"},
            follow=True,
        )

        another_user = User.objects.get(email="b@b.com")
        self.assertIn(another_user, list_.shared_with.all())
