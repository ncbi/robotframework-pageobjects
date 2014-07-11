from po import selectors_page
import unittest
from robotpageobjects.exceptions import SelectorError

class FindElementsTestCase(unittest.TestCase):
    def setUp(self):
        self.page = selectors_page.Page()
        self.page.open()

    def test_find_elements(self):
        self.assertEqual(len(self.page.find_elements("search-button")), 1, "search-button should locate one element.")

    def test_find_element(self):
        failed = False
        try:
            self.page.find_element("search-button")
        except ValueError:
            failed = True

        self.assertFalse(failed, "search-button should locate an element.")

    def test_find_element_multiple(self):
        failed = False
        try:
            self.page.find_element("inputs")
        except SelectorError:
            failed = True

        self.assertTrue(failed, "find_element should throw an error if matches multiple elements")


    def tearDown(self):
        self.page.close()

if __name__ == "__main__":
    unittest.main()