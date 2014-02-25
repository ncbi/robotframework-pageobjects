import unittest
from po import widget_relative_url


class TestWidgetSearch(unittest.TestCase):

    def test_search(self):

        widget_page = widget_relative_url.Page()
        widget_page.open()
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_search_result_page.close()

unittest.main()
