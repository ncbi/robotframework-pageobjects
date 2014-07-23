from google import GoogleHomePage
import unittest


class GoogleTestCase(unittest.TestCase):

    def setUp(self):
        self.google_homepage = GoogleHomePage()
        self.google_homepage.open()

    def test_first_result_page_title_should_contain_search_term(self):
        search_result_page = self.google_homepage.search_for("cat")
        self.destination_page = search_result_page.click_result(1)
        self.destination_page.title_should_contain("cat")

    def tearDown(self):
        self.destination_page.close()

if __name__ == "__main__":
    unittest.main()
