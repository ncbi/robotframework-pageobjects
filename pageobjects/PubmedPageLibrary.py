from pageobjects.base.EntrezPageLibrary import robot_alias, EntrezPageLibrary
from BooksPageLibrary import BooksPageLibrary


class PubmedPageLibrary(EntrezPageLibrary):
    name = "pubmed"
    homepage = "/pubmed"

    @robot_alias("find_related_data_from__name__in")
    def find_related_data_in(self, dbname):
        self.se.wait_until_element_is_visible("rdDatabase")
        self.se.select_from_list_by_value("rdDatabase", dbname)
        self.se.wait_until_page_contains("NCBI Bookshelf books that cite the current articles")
        self.se.click_button("rdFind")

        # For demo purpose, hardcode the type of page returned
        return BooksPageLibrary()
