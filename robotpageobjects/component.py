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

    @not_keyword
    def get_instance(self, component_class, locator):

        """ Gets a page component's instance.
        Use when you know you will be returning one
        instance of a component. If there are none on the page,
        returns None.

        :param component_class: The page component class
        """

        els = self.get_instances(component_class, locator)
        try:
            ret = els[0]
        except KeyError:
            ret = None

        return ret

    @not_keyword
    def get_instances(self, component_class, locator):

        """ Gets a page component's instances as a list
        Use when you know you will be returning at least two
        instances of a component. If there are none on the page
        returns an empty list.

        :param component_class: The page component class
        """
        return [component_class(reference_webelement) for reference_webelement in
                self.get_reference_elements(locator)]

    @not_keyword
    def get_reference_elements(self, locator):
        """
        Get a list of reference elements associated with the component class.
        :param component_class: The page component class
        """

        # TODO: Yuch. If we call find_element, we get screenshot warnings relating to DCLT-659, DCLT-726,
        # browser isn't open yet, and when get_keyword_names uses inspect.getmembers, that calls
        # any methods defined as properties with @property, but the browser isn't open yet, so it
        # tries to create a screenshot, which it can't do, and thus throws warnings. Instead we call
        # the private _element_find, which is not a keyword.

        component_elements = self._element_find(locator, False, True)
        return component_elements