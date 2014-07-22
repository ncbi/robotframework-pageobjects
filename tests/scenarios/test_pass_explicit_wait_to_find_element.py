import unittest
from po.widget_rel_uri_attr import Page
from nose.tools import raises


class ImplicitWaitTestCase(unittest.TestCase):

    def setUp(self):
        self.p = Page()
        self.p.open()

    @raises(ValueError)
    def test_pass_explicit_wait_to_find_element(self):
        self.p.click_delayed_content_button()
        self.p.delayed_content_should_exist_explicit()

    @raises(ValueError)
    def test_pass_explicit_wait_to_find_elements(self):
        self.p.click_delayed_content_button()
        self.p.delayed_content_should_exist_explicit_calling_find_elements()

    def tearDown(self):
        self.p.close()

if __name__ == "__main__":
    unittest.main()

