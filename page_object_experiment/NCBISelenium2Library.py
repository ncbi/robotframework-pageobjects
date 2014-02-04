from Selenium2Library import Selenium2Library


class NCBISelenium2Library(Selenium2Library):

    def click_docsum_item_number(self, n):
        i = int(n) + 1
        self.click_link("xpath=//div[@class='rprt'][%s]//p[@class='title']/a" % str(i))
