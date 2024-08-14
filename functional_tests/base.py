import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

MAX_WAIT = 10


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except(AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)
    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(
            options=chrome_options,
        )
        staging_server = os.getenv("STAGING_SERVER")
        if staging_server:
            self.live_server_url = f"http://{staging_server}"

    def tearDown(self):
        self.browser.quit()

    @wait
    def wait_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(row_text, [row.text for row in rows])

    @wait
    def wait_for(self, fn):
        return fn()

    def get_item_input_box(self):
        return self.browser.find_element(By.ID, "id_text")

    @wait
    def wait_to_be_logged_in(self, email):
        self.browser.find_element(By.LINK_TEXT, "Log out"),
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")
        self.assertIn(email, navbar.text)

    @wait
    def wait_to_be_logged_out(self, email):
        self.browser.find_element(By.NAME, "email")
        navbar = self.browser.find_element(By.CLASS_NAME, "navbar")
        self.assertNotIn(email, navbar.text)
