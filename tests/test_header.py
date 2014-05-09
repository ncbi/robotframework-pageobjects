from robotpageobjects import Page, Component, ComponentManager, robot_alias
from robot.utils import asserts
import unittest
import os



""" The following classes are used by tests for the header/subheader component.
These tests are at the end of the file and are ultimately intended for the actual header/subheader
components that will be written at some point soon. For now, I am sticking them in the
Robot Framework Page Object package because it's a proof-of-concept and since the packages
aren't written yet and the version of RF PO with support for components isn't tagged yet, I
don't want to have to link to dev branches in depdendency links.
"""

class SubHeaderComponent(Component):
    """ Encapsulates the common, Sub header
    found on most NCBI pages.
    """

    # This identifies the parent
    # web element for this component.
    locator = "css=.header"

    # All selectors are implicitly limited to
    # descendents of the "root webelement" for
    # this component. This assures that you are finding
    # the element for **this** component.
    # If for some reason, you need to access the actual
    # root WebElement for this instance, access: self.root_webelement
    # from a component method.
    selectors = {
        "Search Database Select": "id=database",
        "Search Term Input": "id=term",
        "Search Button": "id=search",
    }

    # As a rule, allow easy access
    # as properties, instead of getter
    # methods.
    @property
    def selected_database(self):
        # Remember, try to use Selenium2Library methods, instead of
        # the lower level WebDriver API. You can pass selectors to
        # these as well as locators.
        return self.get_selected_list_label("Search Database Select")

    def search(self, db, term):
        self.select_from_list_by_label("Search Database Select", db)
        self.input_text("Search Term Input", term)
        self.click_button("Search Button")
        # Let the page object return the correct page object
        # after calling this method on the GlobalHeader instance.



class SubHeaderComponentManager(ComponentManager):

    # The job of the manager class is to allow the
    # page object access to the component instances.
    # Here, since there is only one GlobalHeader per page
    # we define a single property, called "subheader"
    # and return the result of get_instance(). If
    # there were multiple instances on the page, we'd
    # call get_instances().
    @property
    def subheader(self):
        return self.get_instance(SubHeaderComponent)


class HeaderComponent(Component, SubHeaderComponentManager):

    locator = "id=universal_header"

    selectors = {
        "logo": "css=.ncbi_logo",

    }

    def click_logo(self):
        self.click_element("logo")

    def search(self, db, term):

        # Defers to this component's sub component
        self.subheader.search(db, term)
        # Should return a page object here, but this is just for testing.


class HeaderComponentManager(ComponentManager):

    @property
    def header(self):
        return self.get_instance(HeaderComponent)


class MySubHeaderPage(Page, SubHeaderComponentManager):

    uri = "/"

    @robot_alias("selected_database_in_subheader_should_be_on__name__")
    def selected_database_in_subheader_should_be(self, db):
        asserts.assert_equals(self.subheader.selected_database, db)

    @robot_alias("search_from_subheader_on__name__")
    def search_from_subheader(self, db, term):
        self.subheader.search(db, term)
        # Here we'd have to figure out what page object to return...


class MyHeaderPage(Page, HeaderComponentManager):
    uri = "/"

    def search_from_header(self, db, term):
        self.header.search(db, term)

class SubHeaderComponentTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        #os.environ["PO_BROWSER"] = "firefox"
        os.environ["PO_SELENIUM_SPEED"] = "0"
        self.sub_header_page = MySubHeaderPage()
        self.sub_header_page.open()

    def test_selected_database(self):
        self.sub_header_page.selected_database_in_subheader_should_be("All Databases")

    def test_search_from_subheader(self):
        self.sub_header_page.search_from_subheader("Books", "dog")
        self.sub_header_page.title_should_be("dog - Books - NCBI")

    def tearDown(self):
        self.sub_header_page.close()

class HeaderComponentTestCase(unittest.TestCase):

    def setUp(self):
        os.environ["PO_BASEURL"] = "http://www.ncbi.nlm.nih.gov"
        #os.environ["PO_BROWSER"] = "firefox"
        os.environ["PO_SELENIUM_SPEED"] = "0"
        self.header_page = MyHeaderPage()
        self.header_page.open()

    def test_delegated_search_from_subheader(self):
        self.header_page.search_from_header("Books", "dog")
        self.header_page.title_should_be("dog - Books - NCBI")

    def tearDown(self):
        self.header_page.close()
