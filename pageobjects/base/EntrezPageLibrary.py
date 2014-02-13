from PageObjectLibrary import robot_alias, PageObjectLibrary

        
class EntrezPageLibrary(PageObjectLibrary):
    """
    This is the base class for PubmedPageLibrary, BooksPageLibrary, etc.
    """

    @robot_alias("click__name__docsum_item")
    def click_docsum_item(self, n):
        i = int(n) + 1
        self.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))
        return self

    def search(self, term):
        self.input_text("term", term)
        self.click_button("search")
        return self

