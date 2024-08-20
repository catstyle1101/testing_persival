from unittest import skip

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest


class ItemValidationTest(FunctionalTest):
    def get_error_element(self):
        return self.browser.find_element(By.CLASS_NAME, "has-error")

    def test_cannot_add_empty_list_elements(self):
        """Тест: нельзя добавлять пустые элементы списка."""
        # Эдит открывает домашнюю страницу и случайно пытается отправить пустой
        # элемент списка. Она нажимает Enter на пустом поле ввода.
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Домашняя страница обновляется и появляется сообщение об ошибке,
        # которое говорит, что элементы списка не должны быть пустыми.
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid"),
        )

        # Она пробует снова, теперь с неким текстом для элемента, и теперь это работает.
        self.get_item_input_box().send_keys("Купить молока.")
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:valid"),
        )
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Купить молока.")

        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Она получает аналогичное предупреждение на странице списка.
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:invalid"),
        )

        # И она может его исправить, заполнив поле неким текстом.
        self.get_item_input_box().send_keys("Сделать чай.")
        self.wait_for(
            lambda: self.browser.find_element(By.CSS_SELECTOR, "#id_text:valid"),
        )
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Купить молока.")
        self.wait_for_row_in_list_table("2: Сделать чай.")

    def test_cannot_add_duplicate_items(self):
        # Эдит открывает домашнюю страницу и начинает новый список
        self.browser.get(self.live_server_url)
        self.add_list_item("Buy wellies")

        # Она случайно пытается ввести повторяющийся элемент
        self.get_item_input_box().send_keys("Buy wellies")
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Она видит полезное сообщение об ошибке
        self.wait_for(
            lambda: self.assertEqual(
                self.get_error_element().text,
                "You've already got this in your list",
            )
        )

    def test_error_messages_are_cleared_on_input(self):
        # Эдит начинает список и вызывает ошибку валидации:
        self.browser.get(self.live_server_url)
        self.add_list_item("Banter to thick")
        self.get_item_input_box().send_keys("Banter to thick")
        self.get_item_input_box().send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertTrue(self.get_error_element().is_displayed()))

        # Она начинает набирать в поле ввода, чтобы очистить ошибку
        self.get_item_input_box().send_keys("a")

        # Она довольна от того, что сообщение об ошибке исчезает
        self.wait_for(lambda: self.assertFalse(self.get_error_element().is_displayed()))
