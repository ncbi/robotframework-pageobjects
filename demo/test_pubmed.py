from pubmed import PubmedHomePage
import unittest


class PubmedTestCase(unittest.TestCase):

    def setUp(self):
        self.pubmed_homepage = PubmedHomePage()
        self.pubmed_homepage.open()

    def test_first_result_page_body_should_contain_search_term(self):
        pubmed_docsum_page = self.pubmed_homepage.search_for("cat")
        self.article_page = pubmed_docsum_page.click_result(1)
        self.article_page.body_should_contain("cat")

    def tearDown(self):
        self.article_page.close()

if __name__ == "__main__":
    unittest.main()
