import re

from django.core import mail
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest

TEST_EMAIL = "edith@example.com"
SUBJECT = "Your login link for Superlists"


class LoginTest(FunctionalTest):
    def test_get_an_email_link_to_log_in(self):
        # Эдит заходит на сайт суперсписков и впервые
        # замечает раздел "войти" в навигационной панели
        # Он говорит ей ввести свой адрес электронной почты, что она и делает
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.NAME, "email").send_keys(TEST_EMAIL)
        self.browser.find_element(By.NAME, "email").send_keys(Keys.ENTER)

        # Появляется сообщение, что ей на почту было выслано письмо
        self.wait_for(
            lambda: self.assertIn(
                "Check your email for your login link",
                self.browser.find_element(By.TAG_NAME, "body").text,
            )
        )

        # Эдит проверяет свою почту и находит сообщение

        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(SUBJECT, email.subject)

        # Оно содержит ссылку на url-адрес
        self.assertIn("Use this link to log in:", email.body)
        url_search = re.search(r"(https?://[^\s]+)", email.body)
        if not url_search:
            self.fail(f"Could not find url in email body:\n{email.body}")
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Эдит нажимает на ссылку
        self.browser.get(url)

        # Она зарегистрирована в системе!
        self.wait_to_be_logged_in(email=TEST_EMAIL)

        # Теперь она выходит из системы
        self.browser.find_element(By.LINK_TEXT, "Log out").click()

        # Она вышла из системы
        self.wait_to_be_logged_out(email=TEST_EMAIL)
