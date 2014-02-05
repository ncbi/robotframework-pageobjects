import unittest
from PubmedPageLibrary import PubmedPageLibrary

class TestPubmedflows(unittest.TestCase):

    def test_pubmed_to_books(self):
        pubmed_page = PubmedPageLibrary().open()
        pubmed_page.search_pubmed_for("breast cancer")
        books_page = pubmed_page.find_related_data("books")
        books_page.click_books_docsum_item_number(0)
        books_page.click_table_of_contents()
        books_page.close()
