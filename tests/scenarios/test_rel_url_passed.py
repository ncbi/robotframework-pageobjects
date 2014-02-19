import unittest
from po import widget_no_homepage


class TestWidgetSearch(unittest.TestCase):

    def test_search(self):

        widget_page = widget_no_homepage.Page()
        widget_page.open("/pages/widget-home-page.html")
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        try:
            self.widget_search_result_page.close()
        except AttributeError:
            pass

unittest.main()
