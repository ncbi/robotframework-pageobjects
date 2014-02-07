from page_objects.common.EntrezPageLibrary import EntrezPageLibrary


class BooksPageLibrary(EntrezPageLibrary):
    name = "books"
    homepage = "http://www.ncbi.nlm.nih.gov/books"

    def click_table_of_contents(self):
        self.se.click_link("Table of contents")
        return self
        
    #__metaclass__ = EntrezPageLibraryMeta
