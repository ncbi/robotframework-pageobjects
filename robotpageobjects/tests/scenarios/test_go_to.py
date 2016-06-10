import unittest
from robotpageobjects.tests.scenarios.po import widget_template
from robotpageobjects import Page


class TestWidgetItem(unittest.TestCase):

    def test_widget_item(self):
        self.widget_item_page = widget_template.WidgetItemPage()
        self.widget_item_page.open_browser("http://www.google.com", "phantomjs")
        self.widget_item_page.go_to({"category": "home-and-garden", "id": "123"})
        self.widget_item_page.title_should_be("Cool Widget")

    def test_no_uri_template(self):
        self.p = Page()
        self.p.baseurl = 'https://www.google.com/'
        self.p.open()
        self.p.title_should_be('Google')

    def tearDown(self):
        try:
            self.widget_item_page.close()
        except AttributeError:
            pass

if __name__ == "__main__":
    unittest.main()
