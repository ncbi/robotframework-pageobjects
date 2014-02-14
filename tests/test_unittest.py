import unittest
import widget


class TestGoogleSearch(unittest.TestCase):

    def test_search(self):
        widget_page = widget.Page().open()
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_search_result_page.close()

unittest.main()
