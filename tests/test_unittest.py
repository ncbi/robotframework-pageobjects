import unittest
import widget


class TestGoogleSearch(unittest.TestCase):

    def setUp(self):
        self.widget_page = widget.Page().open()

    def test_search(self):
        widget_result_page = self.widget_page.search("search term")
        widget_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_page.close()

unittest.main()
