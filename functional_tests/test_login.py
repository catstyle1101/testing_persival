import os
import poplib
import re
import time

from django.core import mail
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from functional_tests.base import FunctionalTest

SUBJECT = "Your login link for Superlists"


class LoginTest(FunctionalTest):
    def test_get_an_email_link_to_log_in(self):
        # Эдит заходит на сайт суперсписков и впервые
        # замечает раздел "войти" в навигационной панели
        # Он говорит ей ввести свой адрес электронной почты, что она и делает
        if self.staging_server:
            test_email = "edith.testuser@yahoo.com"
        else:
            test_email = "edith@example.com"
        self.browser.get(self.live_server_url)
        self.browser.find_element(By.NAME, "email").send_keys(test_email)
        self.browser.find_element(By.NAME, "email").send_keys(Keys.ENTER)

        # Появляется сообщение, что ей на почту было выслано письмо
        self.wait_for(
            lambda: self.assertIn(
                "Check your email for your login link",
                self.browser.find_element(By.TAG_NAME, "body").text,
            )
        )

        # Эдит проверяет свою почту и находит сообщение
        body = self.wait_for_email(test_email, SUBJECT)

        # Оно содержит ссылку на url-адрес
        self.assertIn("Use this link to log in:", body)
        url_search = re.search(r"(https?://[^\s]+)", body)
        if not url_search:
            self.fail(f"Could not find url in email body:\n{body}")
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Эдит нажимает на ссылку
        self.browser.get(url)

        # Она зарегистрирована в системе!
        self.wait_to_be_logged_in(email=test_email)

        # Теперь она выходит из системы
        self.browser.find_element(By.LINK_TEXT, "Log out").click()

        # Она вышла из системы
        self.wait_to_be_logged_out(email=test_email)

    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(subject, email.subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL("pop.mail.yahoo.com")
        try:
            inbox.user(test_email)
            inbox.pass_(os.getenv("YAHOO_PASSWORD"))
            while time.time() - start < 60:
                count, _ = inbox.stat()
                for i in reversed(range(max(1, count - 10), count + 1)):
                    print("getting msg", i)
                    _, lines, _ = inbox.retr(i)
                    lines = [l.decode("utf-8") for l in lines]
                    print(lines)
                    if f"Subject: {subject}" in lines:
                        email_id = i
                        body = "\n".join(lines)
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)
            inbox.quit()
