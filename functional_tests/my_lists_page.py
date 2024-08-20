from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class MyListsPage:
    def __init__(self, test: "WebDriver()"):
        self.test = test

    def go_to_my_lists_page(self):
        self.test.browser.get(self.test.live_server_url)
        self.test.browser.find_element(By.LINK_TEXT, "My lists").click()
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.test.browser.find_element(By.TAG_NAME, "h1").text,
                "My lists",
            )
        )
        return self
