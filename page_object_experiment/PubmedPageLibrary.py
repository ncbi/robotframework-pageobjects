from EntrezPageLibrary import EntrezPageLibrary


class PubmedPageLibrary(EntrezPageLibrary):

    def find_related_data(self, dbname):
        self.browser.wait_until_element_is_visible("rdDatabase")
        self.browser.select_from_list_by_value("rdDatabase", dbname)
        self.browser.wait_until_page_contains("NCBI Bookshelf books that cite the current articles")
        self.browser.click_button("rdFind")


