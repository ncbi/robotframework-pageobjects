from EntrezPageLibrary import EntrezPageLibrary


class BooksPageLibrary(EntrezPageLibrary):

    def click_table_of_contents(self):
        self.browser.click_link("Table of contents")