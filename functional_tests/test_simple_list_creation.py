from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest


class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_for_one_user(self):
        # Эдит слышала про крутое новое онлайн-приложение со списком
        # неотложных дел. Она решает оценить его домашнюю страницу
        self.browser.get(self.live_server_url)

        # Она видит, что заголовок и шапка страницы говорят о списках
        # неотложных дел
        self.assertIn("To-Do lists", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do list", header_text)

        # Ей сразу же предлагается ввести элемент списка
        input_box = self.get_item_input_box()
        self.assertEqual(
            input_box.get_attribute("placeholder"),
            "Enter a to-do item",
        )

        # Она набирает в текстовом поле "Купить павлиньи перья"
        # (ее хобби – вязание рыболовных мушек)
        input_box.send_keys("Купить павлиньи перья")

        # Когда она нажимает enter, страница обновляется, и теперь страница
        # содержит "1: Купить павлиньи перья" в качестве элемента списка
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Купить павлиньи перья")

        # Текстовое поле по-прежнему приглашает ее добавить еще один элемент.
        # Она вводит "Сделать мушку из павлиньих перьев"
        # (Эдит очень методична)
        input_box = self.get_item_input_box()
        input_box.send_keys("Сделать мушку из павлиньих перьев")
        input_box.send_keys(Keys.ENTER)

        # Страница снова обновляется и теперь показывает оба элемента
        # ее списка
        self.wait_for_row_in_list_table("1: Купить павлиньи перья")
        self.wait_for_row_in_list_table("2: Сделать мушку из павлиньих перьев")
        # Удовлетворенная, она снова ложится спать.

    def test_multiple_users_can_start_lists_at_different_urls(self):
        """Тест: многочиесленные пользователи могут начать списки по разным url."""
        # Эдит начинает новый список
        self.browser.get(self.live_server_url)
        input_box = self.get_item_input_box()
        input_box.send_keys("Купить павлиньи перья")
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Купить павлиньи перья")

        # Она замечает, что ее список имеет уникальный URL адрес
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, "/lists/.+")

        # Теперь новый пользователь Фрэнсис приходит на сайт.

        ## Мы используем новый сеанс браузера, тем самым обеспечивая, чтобы никакая
        ## Информация от Эдит не прошла через данные cookie и пр.
        self.browser.quit()
        # self.browser = webdriver.Chrome()
        self.setUp()
        # Фрэнсис посещает домашнюю страницу. Нет никаких признаков списка Эдит.
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Купить павлиньи перья", page_text)
        self.assertNotIn("Сделать мушку из павлиньих перьев", page_text)

        # Фрэнсис начинает новый список, вводя новый элемент. Он менее
        # интересен, чем список Эдит...
        input_box = self.get_item_input_box()
        input_box.send_keys("Купить молоко")
        input_box.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Купить молоко")

        # Фрэнсис получает уникальный URL адрес
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, "/lists/.+")
        self.assertNotEqual(edith_list_url, francis_list_url)

        # Опять-таки, нет ни следа от списка Эдит.
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Купить павлиньи перья", page_text)
        self.assertNotIn("Сделать мушку", page_text)

        # Удовлетворенные они оба ложатся спать.
