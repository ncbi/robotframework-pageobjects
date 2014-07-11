from page import ElementFinder, _BaseActions, not_keyword


class _ComponentElementFinder(ElementFinder):
    """Overrides the element finder class that SE2Lib's
    _element_find uses so that we can pass the reference webelement
    instead of the driver. This allows us to limit our DOM search
    in components to the "reference webelement" instead of searching
    globally on the driver instance.
    """

    def __init__(self, webelement):

        super(_ComponentElementFinder, self).__init__()
        self._reference_webelement = webelement

    def find(self, browser, locator, tag=None):
        prefix = self._parse_locator(locator)[0]
        if prefix == "dom":
            return super(_ComponentElementFinder, self).find(browser, locator, tag=tag)
        else:
            return super(_ComponentElementFinder, self).find(self._reference_webelement, locator, tag=tag)


class Component(_BaseActions):
    def __init__(self, reference_webelement, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
        self.reference_webelement = reference_webelement

        # Pass the root webelement to our overridden component finder class.
        self._element_finder = _ComponentElementFinder(self.reference_webelement)
        self.name = self.__class__.__name__


class ComponentManager(_BaseActions):

    def __init__(self, *args, **kwargs):
        super(ComponentManager, self).__init__(*args, **kwargs)
        self.name = self.__class__.__name__

