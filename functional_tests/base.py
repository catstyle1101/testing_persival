import os
import time
from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model, SESSION_KEY, BACKEND_SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from .server_tools import reset_database

MAX_WAIT = 10
SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "screendumps"
)
User = get_user_model()


def wait(fn):
    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                return fn(*args, **kwargs)
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(
            options=chrome_options,
        )
        self._options = chrome_options
        self.staging_server = os.getenv("STAGING_SERVER")
        if self.staging_server:
            self.live_server_url = f"http://{self.staging_server}"
            reset_database(self.staging_server)

    def tearDown(self):
        if (
            len(self._outcome.result.failures) > 0
            or len(self._outcome.result.errors) > 0
        ):
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._window_id = ix
                self.browser.switch_to.window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

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

    def add_list_item(self, item_text):
        num_rows = len(
            self.browser.find_elements(By.CSS_SELECTOR, "#id_list_table tr"),
        )
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f"{item_number}: {item_text}")

    def take_screenshot(self):
        filename = self._get_filename() + ".png"
        print("Taking screenshot", filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + ".html"
        print("Dumping HTML", filename)
        with open(filename, "w") as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(":", ".")[:19]
        return "{folder}/{classname}.{method}-window{window_id}-{timestamp}".format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            window_id=self._window_id,
            timestamp=timestamp,
        )

    def create_pre_authenticated_session(self, email):
        user = User.objects.get_or_create(email=email)[0]
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()
        return session.session_key
