from po import selectors_page
import unittest

class SelectorExceptionsTestCase(unittest.TestCase):
    def setUp(self):
        self.page = selectors_page.Page()
        self.page.open()

    def test_bad_selector(self):
        found = False
        try:
            self.page.find_element("foobar")
        except ValueError, e:
            msg_found = e.message.find("not in the selectors dict") != -1
        self.assertTrue(msg_found,
                        "ValueError should detect that the locator looks like a selector.")

    def test_no_selector(self):
        msg_found = False
        try:
            self.page.find_element("xpath=asdf")
        except ValueError, e:
            msg_found = e.message.find("did not match any elements") != -1
        self.assertTrue(msg_found, "ValueError should detect that the locator looks like a locator.")

    def tearDown(self):
        self.page.close()

if __name__ == "__main__":
    unittest.main()