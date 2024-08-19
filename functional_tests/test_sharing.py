from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .base import FunctionalTest


def quit_if_possible(browser):
    try:
        browser.quit()
    except:
        pass


class SharingTest(FunctionalTest):
    def test_can_share_with_another_user(self):
        # Эдит является зарегистрированным пользователем
        self.create_pre_authenticated_session("edith@example.com")
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Ее друг Анцифер тоже зависает на сайте списков
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        oni_browser = webdriver.Chrome(
            options=chrome_options,
        )
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.create_pre_authenticated_session("oniciferous@example.com")

        # Эдит открывает домашнюю страницу и начинает новый поиск
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        self.add_list_item("Get help")

        # Она замечает опцию "поделиться этим списком"
        share_box = self.browser.find_element(
            By.CSS_SELECTOR,
            "input[name='share']",
        )
        self.assertEqual(
            share_box.get_attribute("placeholder"),
            "your-friend@example.com",
        )
