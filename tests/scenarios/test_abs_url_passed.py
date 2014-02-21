import unittest
from po import widget_no_homepage
import os


class TestWidgetSearch(unittest.TestCase):

    widget_url = "file:///%s" % os.path.dirname(os.path.abspath(__file__)) + os.sep + os.path.join("site", "index.html").replace("\\", "/")
    
    def test_search(self):
        widget_page = widget_no_homepage.Page()
        widget_page.open(self.widget_url)
        self.widget_search_result_page = widget_page.search("search term")
        self.widget_search_result_page.should_have_results(3)

    def tearDown(self):
        self.widget_search_result_page.close()


unittest.main()
