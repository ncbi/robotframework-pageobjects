import unittest
from po import widget_template


class TestWidgetItem(unittest.TestCase):

    def test_widget_item(self):
        self.widget_item_page = widget_template.WidgetItemPage()
        self.widget_item_page.open(category="home-and-garden", id="123")
        self.widget_item_page.title_should_be("Cool Widget")

    def tearDown(self):
        try:
            self.widget_item_page.close()
        except AttributeError:
            pass

unittest.main()
