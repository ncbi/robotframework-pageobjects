
from NCBISelenium2Library import NCBISelenium2Library

class PubmedLibrary(object):

    def __init__(self):
        self.browser = NCBISelenium2Library._se_instance

    def get_pubmed_title(self):
        return self.browser.get_title()