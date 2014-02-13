import os

import robot.utils.asserts as asserts

from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias


class Page(PageObjectLibrary):
    name = "Widget Page"
    homepage = "file://" + os.path.dirname(os.path.realpath(__file__)) + "/pages/widget-home-page.html"

    @robot_alias("search__name__for")
    def search(self, term):
        self._se.input_text("q", "search term")
        self._se.click_element("go")
        return ResultPage()


class ResultPage(Page):
    name = "Widget Search Result Page"

    @robot_alias("__name__should_have_results")
    def should_have_results(self, expected):
        len_results = len(self._find_element("xpath=id('results')/li", False, False))
        asserts.assert_equals(len_results, int(expected), "Unexpected number of results found on %s, got %s, "
                                                         "expected %s" %(
            self.name, len_results, expected))


