import unittest
from robotpageobjects.tests.scenarios.po import widget_rel_uri_attr

class TestWidgetSearch(unittest.TestCase):

    def test_screen_shot(self):

        self.widget_page = widget_rel_uri_attr.Page()
        self.widget_page.open()
        self.widget_page.capture_page_screenshot()

    def tearDown(self):
        self.widget_page.close()

unittest.main()
