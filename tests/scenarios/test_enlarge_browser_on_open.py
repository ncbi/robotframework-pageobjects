import unittest
from po import widget_template


class TestBrowserOpen(unittest.TestCase):

    def test_browser_enlarge_on_open(self):
        self.widget_item_page = widget_template.WidgetItemPage()
        self.widget_item_page.open({"category": "home-and-garden", "id": "123"})
        window_size = self.widget_item_page.get_current_browser().get_window_size()
        expected_window_size = {'width':1920, 'height':1080}
        self.assertEqual(window_size, expected_window_size, "Window size should be 1920x1080")

    def tearDown(self):
        try:
            self.widget_item_page.close()
        except AttributeError:
            pass

if __name__ == "__main__":
    unittest.main()
