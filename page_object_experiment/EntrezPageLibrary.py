from PageObjectLibrary import PageObjectLibrary


class EntrezPageLibrary(PageObjectLibrary):

    def click_docsum_item_number(self, n):
        i = int(n) + 1
        self.browser.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))

    def search_for(self, term):
        self.browser.input_text("term", term)
        self.browser.click_button("search")