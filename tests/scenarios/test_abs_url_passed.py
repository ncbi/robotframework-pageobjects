import unittest
from po import widget_no_homepage


class TestWidgetSearch(unittest.TestCase):
    def test_search(self):
        widget_page = widget_no_homepage.Page()
        widget_page.open("file:///Users/cohenaa/PyCharmProjects/rfexp/tests/scenarios/pages/widget-home-page.html")
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_search_result_page.close()


unittest.main()
