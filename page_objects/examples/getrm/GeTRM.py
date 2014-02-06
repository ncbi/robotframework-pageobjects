import sys
from page_objects.PageObjectLibrary import PageObjectLibrary
#from Selenium2Library import Selenium2Library
class GeTRM(PageObjectLibrary):
    browser = "firefox"
    homepage =  "http://www.ncbi.nlm.nih.gov/variation/tools/get-rm"
    def clear_element(self, locator):
        element = self.se._element_find(locator, True, True)
        element.clear()
        
    def get_values(self, locator, tag=None):
        element = self.se._elements_find(locator, False, False, tag=tag)
        if element is None:
            return None
        elif not isinstance(element, list) and not isinstance(element, tuple):
            return element.get_attribute("value")
        else:
            return reduce(lambda val1, val2: val1 + val2, [el.get_attribute("value") for el in element])
    
    def __init__(self, *args, **kwargs):
        super(GeTRM, self).__init__(self, *args, **kwargs)
        print self.open