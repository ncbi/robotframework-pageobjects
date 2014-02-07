import unittest
from PubmedPageLibrary import PubmedPageLibrary

class TestPubmedflows(unittest.TestCase):

    def test_pubmed_to_books(self):
        pubmed = PubmedPageLibrary().open()
        pubmed.search("breast cancer")
        books = pubmed.find_related_data_in("books")
        books.click_docsum_item(0)
        books.click_table_of_contents()
        books.close()

unittest.main()
