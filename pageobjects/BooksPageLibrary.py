from pageobjects.base.EntrezPageLibrary import EntrezPageLibrary


class BooksPageLibrary(EntrezPageLibrary):
    name = "books"
    homepage = "http://www.ncbi.nlm.nih.gov/books"

    def click_table_of_contents(self):
        self.click_link("Table of contents")
        return self