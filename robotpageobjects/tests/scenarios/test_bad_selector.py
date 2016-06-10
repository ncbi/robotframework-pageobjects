from robotpageobjects.tests.scenarios.po import selectors_page
from robotpageobjects import exceptions
import unittest

class BadSelectorTestCase(unittest.TestCase):
    def setUp(self):
        self.page = selectors_page.Page()
        self.page.open()

    def test_bad_selector(self):
        found = False
        try:
            self.page.find_element("foobar")
        except exceptions.SelectorError as e:
            msg_found = e.message.find("not a valid locator") != -1
        self.assertTrue(msg_found,
                        "ValueError should detect that the locator looks like a selector.")

    def tearDown(self):
        self.page.close()

if __name__ == "__main__":
    unittest.main()
