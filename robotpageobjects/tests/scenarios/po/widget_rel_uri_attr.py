
import robot.utils.asserts as asserts
from robotpageobjects.page import Page, robot_alias

class Page(Page):
    name = "Widget Page"

    uri = "/site/index.html"

    selectors = {
        "search button": "go",
        "search box": "q",
        "another paragraph": "css=div.{klass} p#{id}",
        "delayed content button": "id=delayed-content",
        "delayed content holder": "id=delayed-content-holder",
        "delayed content": "css=#delayed-content-holder > p",
        "search form": "xpath=//form",
        "form label": "%(search form)s/label",
    }

    @robot_alias("search__name__for")
    def search(self, term):
        self.input_text("search box", "search term")
        self.click_element("search button")
        return SearchResultPage()

    def click_delayed_content_button(self):
        self.click_button("delayed content button")
        return self

    def delayed_content_should_exist(self):
        text = self.get_text("delayed content")
        asserts.assert_equal(text, "I took about 2 seconds to be inserted")
        return self

    def delayed_content_should_exist_explicit(self):
        # This should raise a ValueError, since we told find_element not to wait.
        text = self.find_element("delayed content", wait=0).text
        asserts.assert_equal(text, "I took about 2 seconds to be inserted")
        return self

    def delayed_content_should_exist_explicit_calling_find_elements(self):
        # This should raise a ValueError, since we told find_element not to wait.
        els = self.find_elements("delayed content", wait=0)
        text = els[0].text
        asserts.assert_equal(text, "I took about 2 seconds to be inserted")
        return self

    def get_templated_selector_element_text(self):
        loc = self.resolve_selector("another paragraph", klass="ct", id="foo" )
        return self.get_text(loc)

    def title_should_be(self, title):
        return super(Page, self).title_should_be(title)


class SearchResultPage(Page):
    name = "Widget Search Result Page"
    selectors = {"results": "xpath=id('results')/li"}

    @robot_alias("__name__should_have_results")
    def should_have_results(self, expected):
        len_results = len(self.find_elements("results"))
        asserts.assert_equal(len_results, int(expected), "Unexpected number of results found on %s, got %s, "
                                                          "expected %s" %(self.name, len_results, expected))
        return self

