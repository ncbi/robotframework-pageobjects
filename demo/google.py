from robotpageobjects import Page, robot_alias
from robot.utils import asserts


class GoogleHomePage(Page):
    """ Models the Google home page """

    name = "Google"
    uri = "/"

    selectors = {
        "search input": "xpath=//input[@name='q']",
        "search button": "xpath=//button[@name='btnG']|//input[@name='btnG']",
    }


    @robot_alias("type_in__name__search_box")
    def type_in_search_box(self, txt):
        self.input_text("search input", txt)
        return self

    @robot_alias("click__name__search_button")
    def click_search_button(self):
        self.click_button("search button")
        return GoogleSearchResultPage()

    @robot_alias("search__name__for")
    def search_for(self, term):
        self.type_in_search_box(term)
        return self.click_search_button()


class GoogleSearchResultPage(Page):
    """Models a Google search result page. For example:
    http://www.google.com/#q=cat """

    uri_template = "/#q={term}"

    selectors = {
        "nth result link": "xpath=(//li[@class='g'])[{n}]//div//h3//a | (//li[@class='g'])[{n}]/h3/a",
    }

    @robot_alias("click_result_on__name__")
    def click_result(self, i):
        locator = self.resolve_selector("nth result link", n=int(i))
        self.click_link(locator)
        return DestinationPage()

class DestinationPage(Page):

    uri_template = "/{path}"

    selectors = {
        "title element": "xpath=//head//title",
    }

    @robot_alias("__name__title_should_contain")
    def title_should_contain(self, str, ignore_case=True):
        ref_str = str.lower() if ignore_case else str
        ref_str = ref_str.encode("utf-8")
        title = self.get_title().encode("utf-8").lower()
        asserts.assert_true(ref_str in title, "%s does not contain %s" %(title, ref_str))
        return self
