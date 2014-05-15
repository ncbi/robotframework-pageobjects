""" This module comtains the GoogleSearchResultComponent class which
represents the DOM structure and functionality
of a single instance of a Google Search Result entry. It also contains
the GoogleSearchResultComponentManager, which is responsible for
locating instances of GoogleSearchResult and attaching them as a list of
search_results on the GoogleSearchResult page object."""

from robotpageobjects import Component, ComponentManager


class GoogleSearchResultComponent(Component):

    # Within a component, selector entries
    # are relative to the component's "reference_element". The
    # A component's reference element is defined by its manager's
    # locator property and is usually a parent webelement of
    # the component, which contains only markup related to the
    # component. But it doesn't have to be. Some components
    # contains elements that don't hae a common unique ancestor.
    # In this case you can create selector entries that use xpath or
    # css strategies, but they should be relative to the reference element.
    selectors = {
        "result title link": "css=div h3 a",
    }

    def utf8(self, txt):
        return txt.encode("utf-8").strip()

    # Especially for components we prefer dynamic properties
    # over getters. For example you'd get the entire text content of
    # the first search result from a page object  method like this:
    # self.search_results[0].text
    @property
    def text(self):
        return self.reference_webelement.text

    @property
    def title(self):
        ret = self.utf8(self.get_text("result title link"))
        return ret

    def go(self):
        """Goes to the this result, by clicking on its link."""
        self.click_link("result title link")


class GoogleSearchResultComponentManager(ComponentManager):

    locator = "xpath=//li[@class='g']"

    # Sets a property called "search_Results" on the page object
    # inheriting form this manager. The list contains instances
    # of all search results on the page.
    @property
    def search_results(self):
        return self.get_instances(GoogleSearchResultComponent)
