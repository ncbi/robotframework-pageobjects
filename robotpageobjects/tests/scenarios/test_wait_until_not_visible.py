import unittest
from robotpageobjects.tests.scenarios.po import selectors_page

class WaitUntilNotVisibleTestCase(unittest.TestCase):

    def setUp(self):
        self.p = selectors_page.Page()
        self.p.open()

    def test_wait_until_element_not_visible(self):
        self.p.click_element("hide-button")
        self.p.wait_until_element_is_not_visible("para-to-be-hidden")
        self.p.element_should_not_be_visible("para-to-be-hidden")

    def test_wait_for_element_not_visible(self):
        self.p.click_element("hide-button")
        self.p.wait_for(lambda: not self.p.is_visible("para-to-be-hidden"))
        self.p.element_should_not_be_visible("para-to-be-hidden")

    def test_wait_until_element_not_visible_throws_exception(self):
        try:
            self.p.click_element("delayed-content-button")
            self.p.wait_until_element_is_not_visible("para-to-be-hidden", 8)
        except Exception as e:
            self.assertTrue(isinstance(e, AssertionError))
            self.assertIn("still matched after", e.message)

    def test_wait_for_element_not_visible_throws_exception(self):
        try:
            self.p.click_element("delayed-content-button")
            self.p.wait_for(lambda: not self.p.is_visible("para-to-be-hidden"), 8, 'Element did not disappear')
        except Exception as e:
            self.assertIn("Element did not disappear", e.msg)

    def tearDown(self):
        self.p.close()

if __name__ == '__main__':
    unittest.main()
