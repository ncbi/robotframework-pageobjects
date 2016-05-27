
import robot.utils.asserts as asserts

from robotpageobjects.page import Page, robot_alias


class SearchResultPage(Page):
    name = "Widget Search Result Page"

    @robot_alias("__name__should_have_results")
    def should_have_results(self, expected):
        len_results = len(self.find_elements("xpath=id('results')/li", required=False))
        asserts.assert_equal(len_results, int(expected), "Unexpected number of results found on %s, got %s, "
                                                         "expected %s" %(
            self.name, len_results, expected))

        return self

class Page(Page):
    name = "Widget Page"

    @robot_alias("search__name__for")
    def search(self, term):
        self.input_text("q", "search term")
        self.click_element("go")

        return SearchResultPage()



