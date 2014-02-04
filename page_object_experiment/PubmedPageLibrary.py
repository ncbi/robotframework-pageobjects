from EntrezPageLibrary import EntrezPageLibrary


class PubmedPageLibrary(EntrezPageLibrary):
    name = "pubmed"
    def find_related_data(self, dbname):
        self.se.wait_until_element_is_visible("rdDatabase")
        self.se.select_from_list_by_value("rdDatabase", dbname)
        self.se.wait_until_page_contains("NCBI Bookshelf books that cite the current articles")
        self.se.click_button("rdFind")
    
    def __init__(self, *args, **kwargs):
        print self.search_pubmed_for("foo")
        return super(PubmedPageLibrary, self).__init__(*args, **kwargs)