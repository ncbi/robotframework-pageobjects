from robotpageobjects.tests.scenarios import po
import unittest
from nose.tools import raises
from robotpageobjects.exceptions import SelectorError


class FindElementsTestCase(unittest.TestCase):
    def setUp(self):
        self.page = po.selectors_page.Page()
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

    @raises(SelectorError)
    def test_find_element_multiple(self):
        self.page.find_element("inputs")

    def test_find_element_webelement(self):
        element_found_by_selector = self.page.find_element("search-button")
        self.page.click_element(element_found_by_selector)
        self.page.location_should_be("/site/result.html?q=search%20term")

    def tearDown(self):
        self.page.close()

if __name__ == "__main__":
    unittest.main()
