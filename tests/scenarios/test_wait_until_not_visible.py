import unittest
from po import selectors_page
from robotpageobjects import base
import time

class WaitUntilNotVisibleTestCase(unittest.TestCase):

    def test_wait_until_element_not_visible(self):
        self.p = selectors_page.Page()
        self.p.open()
        self.p.click_element("remove-button")
        self.p.wait_until_element_is_not_visible("para-to-be-removed")
        self.p.page_should_not_contain_element("para-to-be-removed")
        self.p.close()

    def test_wait_until_element_not_visible_throws_exception(self):
        try:
            self.p = selectors_page.Page()
            self.p.open()
            self.p.click_element("delayed-content-button")
            self.p.wait_until_element_is_not_visible("para-to-be-removed",8)
        except Exception, e:
            self.assertTrue(isinstance(e, AssertionError))
            self.assertIn("still matched after", e.message)
        self.p.close()

if __name__ == '__main__':
    unittest.main()
