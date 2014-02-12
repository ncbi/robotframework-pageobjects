import re

from robot.utils import asserts

from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias

#from Selenium2Library import Selenium2Library

selectors = {
    "search": "id=loc-search",
    "result-arrow": "xpath=//table[contains(@class, 'grid-results')]/tbody/tr[1]/td[@class='ctrl']",
    "header-spans": "css=div.track-header > span",
    "gt-spans": "css=div.gt-right.gt-ruler > span",
    "search-arrow": "css=img.content-search-go"
}


class GeTRMPageLibrary(PageObjectLibrary):
    homepage = "/variation/tools/get-rm"

    def search(self, term):
        rm_search_box = self.find_element(selectors["search"])
        rm_search_box.clear()
        rm_search_box.send_keys(term)
        self.click_element(selectors["search-arrow"])
        self.wait_until_page_contains_element(selectors["result-arrow"])
        return self

    @robot_alias("go_to__name__results")
    def go_to_results(self):
        self.click_element(selectors["result-arrow"])
        return self

    @robot_alias("__name__result_arrow_should_exist")
    def result_arrow_should_exist(self):
        search_arrow = self.find_element(selectors["result-arrow"], required=False)
        asserts.assert_true(search_arrow is not None and search_arrow.is_displayed(), "Search arrow should be visible.")
        return self

    @robot_alias("__name__headers_should_match")
    def headers_should_match(self, expected_value):
        self.wait_for(lambda: self._get_values(selectors["header-spans"]).strip() != "")
        value = self._get_values(selectors["header-spans"])
        search_result = re.search(expected_value, value)
        asserts.assert_true(search_result is not None,
                            "Headers should look like %s but got %s instead" % (expected_value, value))
        return self

    def _get_values(self, locator, tag=None):
        element = self.find_elements(locator, required=False, tag=tag)
        if element is None:
            return ""
        elif not isinstance(element, list) and not isinstance(element, tuple):
            return element.text
        else:
            values = [el.text for el in element]
            try:
                return reduce(lambda val1, val2: val1 + " " + val2, values)
            except:
                return ""
