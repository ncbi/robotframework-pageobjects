from Selenium2Library import Selenium2Library
class GeTRM(Selenium2Library):
    def clear_element(self, locator):
        element = self._element_find(locator, True, True)
        element.clear()
        
    def get_values(self, locator, tag=None):
        element = self._elements_find(locator, False, False, tag=tag)
        if element is None:
            return None
        elif not isinstance(element, list) and not isinstance(element, tuple):
            return element.get_attribute("value")
        else:
            return reduce(lambda val1, val2: val1 + val2, [el.get_attribute("value") for el in element])