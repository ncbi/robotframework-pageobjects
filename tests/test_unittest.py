import unittest
import widget


class TestGoogleSearch(unittest.TestCase):

    def setUp(self):
        self.widget_page = widget.Page().open()

    def test_google_search_to_apple(self):
        self.widget_result_page = self.widget_page.search("search term")

    def tearDown(self):
        self.widget_page.close()

unittest.main()
