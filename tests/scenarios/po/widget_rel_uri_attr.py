
import robot.utils.asserts as asserts
from robotpageobjects.page import Page, robot_alias

class Page(Page):
    name = "Widget Page"

    uri = "/site/index.html"

    selectors = {
        "search-button": "go",
        "another-paragraph": "css=div.{class} p#{id}",
        "delayed content button": "id=delayed-content",
        "delayed content holder": "id=delayed-content-holder",
        "delayed content": "css=#delayed-content-holder > p"

    }

    @robot_alias("search__name__for")
    def search(self, term):
        self.input_text("q", "search term")
        self.click_element("search-button")
        return SearchResultPage()

    def click_delayed_content_button(self):
        self.click_button("delayed content button")
        return self

    def delayed_content_should_exist(self):
        text = self.get_text("delayed content")
        asserts.assert_equals(text, "I took about 2 seconds to be inserted")
        return self

    def get_templated_selector_element_text(self):
        return self.get_text(("another-paragraph", {"class":"ct", "id": "foo"}))

    def get_templated_selector_element_text_wrong__num_vars(self):
        return self.get_text(("another-paragraph", {"foo": "bar", "class":"ct", "id": "foo"}))


class SearchResultPage(Page):
    name = "Widget Search Result Page"
    selectors = {"results": "xpath=id('results')/li"}

    @robot_alias("__name__should_have_results")
    def should_have_results(self, expected):
        len_results = len(self.find_elements("results"))
        asserts.assert_equals(len_results, int(expected), "Unexpected number of results found on %s, got %s, "
                                                          "expected %s" %(self.name, len_results, expected))
        return self

