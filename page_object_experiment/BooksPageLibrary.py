from EntrezPageLibrary import EntrezPageLibrary


class BooksPageLibrary(EntrezPageLibrary):
    name = "books"
    def click_table_of_contents(self):
        self.se.click_link("Table of contents")
        
    #__metaclass__ = EntrezPageLibraryMeta