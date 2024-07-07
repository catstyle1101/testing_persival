import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(
            options=chrome_options,
        )

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        """Wait for the table row to appear."""
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, "id_list_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Эдит слышала про крутое новое онлайн-приложение со списком
        # неотложных дел. Она решает оценить его домашнюю страницу
        self.browser.get(self.live_server_url)

        # Она видит, что заголовок и шапка страницы говорят о списках
        # неотложных дел
        self.assertIn("To-Do lists", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do list", header_text)

        # Ей сразу же предлагается ввести элемент списка
        input_box = self.browser.find_element(By.ID, "id_new_item")
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
        input_box = self.browser.find_element(By.ID, 'id_new_item')
        input_box.send_keys('Сделать мушку из павлиньих перьев')
        input_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # Страница снова обновляется и теперь показывает оба элемента
        # ее списка
        self.wait_for_row_in_list_table("1: Купить павлиньи перья")
        self.wait_for_row_in_list_table("2: Сделать мушку из павлиньих перьев")
        # Эдит интересно, запомнит ли сайт ее список. Далее она видит, что
        # сайт сгенерировал для нее уникальный URL-адрес – об этом
        # выводится небольшой текст с пояснениями.
        self.fail("Закончить тест!")

        # Она посещает этот URL-адрес – ее список по-прежнему там.