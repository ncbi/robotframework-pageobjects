import unittest
from robotpageobjects.tests.scenarios.po import widget_template


class TestWidgetItem(unittest.TestCase):

    def test_is_visible(self):
        self.widget_item_page = widget_template.WidgetItemPage()
        self.widget_item_page.open({"category": "home-and-garden", "id": "123"})
        self.assertTrue(self.widget_item_page.is_visible("title"), "is_visible should find the title")
        self.assertFalse(self.widget_item_page.is_visible("hidden-content"), "is_visible should find that hidden-content is hidden")

    def tearDown(self):
        try:
            self.widget_item_page.close()
        except AttributeError:
            pass

if __name__ == "__main__":
    unittest.main()
