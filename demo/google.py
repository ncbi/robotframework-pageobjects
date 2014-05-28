from robot.utils import asserts
import time
from robotpageobjects import Page


class GoogleHomePage(Page):
    """ Models the Google home page """

    uri = "/"

    selectors = {
        "search input": "xpath=//input[@name='q']",
        "search button": "xpath=//button[@name='btnG']|//input[@name='btnG']",
    }

    def type_in_search_box(self, txt):
        self.input_text("search input", txt)
        return self

    def click_search_button(self):
        self.click_button("search button")
        return GoogleSearchResultPage()

    def search_for(self, term):
        self.type_in_search_box(term)
        return self.click_search_button()


class GoogleSearchResultPage(Page):

    uri_template = "/#q={term}"

    selectors = {
        "result links": "css=li.g div h3 a",
    }

    def click_result(self, i):
        time.sleep(1)
        self.find_elements("result links")[int(i)].click()
        return DestinationPage()


class DestinationPage(Page):

    uri_template = "/{path}"

    def title_should_contain(self, str, ignore_case=True):
        ref_str = str.lower() if ignore_case else str
        title = self.get_title().encode("utf-8").lower()
        asserts.assert_true(ref_str.encode("utf-8") in title)
        return self


