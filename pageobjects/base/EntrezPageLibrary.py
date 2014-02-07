from PageObjectLibrary import robot_alias, PageObjectLibrary

        
class EntrezPageLibrary(PageObjectLibrary):
    """
    This is the base class for PubmedPageLibrary, BooksPageLibrary, etc.
    """

    @robot_alias("click__name__docsum_item")
    def click_docsum_item(self, n):
        i = int(n) + 1
        self.se.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))
        return self

    def search(self, term):
        self.se.input_text("term", term)
        self.se.click_button("search")
        return self

