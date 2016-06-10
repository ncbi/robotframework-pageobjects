import unittest
from robotpageobjects.tests.scenarios.po import widget_rel_uri_attr


class TestWidgetSearch(unittest.TestCase):

    def test_search(self):

        widget_page = widget_rel_uri_attr.Page()
        widget_page.open()
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_search_result_page.close()

if __name__ == "__main__":
    unittest.main()
