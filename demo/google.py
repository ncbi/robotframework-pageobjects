""" This module contains the 2 page objects that test_google.robot uses:
- GoogleHomePage
- GoogleResultPage
"""

from robotpageobjects import Page, robot_alias
from robot.utils import asserts

from googlesearchresultcomponent import GoogleSearchResultComponentManager


class GoogleHomePage(Page):
    """ A class abstracting the Google home page
    """

    # A Base URL must always be set using either
    # the --variable option or a variable file in
    # Robot Framework. So the home page is at root.
    uri = "/"

    # Let's call this page "Google" instead of the default,
    # "Google Home Page" in Robot keywords.
    name = "Google"

    selectors = {
        "search box": "xpath=//input[@name='q']",

        # The search button is marked up differently depending on the user-agent.
        # For example, PhantomJS gets an input, not a button.
        "search button": "xpath=//button[@name='btnG']|//input[@name='btnG']",
    }

    def type_in_search_box(self, q):
        """Types query into main search box
        :param q: The search query """

        self.input_text("search box", q)

    def click_search_button(self):
        """Clicks the main search button"""

        self.click_button("search button")

    @robot_alias("search__name__for")
    def search_for(self, q):
        """Searches for a query
        :param q: The search query"""

        self.type_in_search_box(q)
        self.click_search_button()

        # If a page object method takes us to
        # another page type, return that page type.
        return GoogleSearchResultPage()


class GoogleSearchResultPage(Page, GoogleSearchResultComponentManager):
    """ Represents a Google result page. We inherit from
    GoogleResultComponentManager, which is responsible for
    finding and attaching Google result components to this page
    instance and is accessed by "self.results". Each result instance
    represents the DOM structure and functionality of a single Google
    result listing.
    """

    # Google uses hashes and gets content via AJAX.
    # so http://www.google.com/#q=cat is the search result
    # page when we search for "cat".
    uri_template = "#q={q}"

    # Use the robot_alias decorator to tell Robot how this method
    # should be traslated into a keyword. By default, methods get
    # the name of the page object (with spaces replacing capitals)
    # appended to the method name, but we can change that with this
    # decorator. The "__name__" token tells Robot where to put the
    # page object name.
    @robot_alias("all_result_titles_on__name__should_contain")
    def all_results_should_contain(self, expected_text):
        """Asserts that all google result titles have specified text
        :param text: The expected text"""

        # This wait won't be necessary after resolving https://jira.ncbi.nlm.nih.gov/browse/QAR-47914
        self.wait_until_page_contains_element(GoogleSearchResultComponentManager.locator)
        asserts.assert_true(all([expected_text in result.text.lower() for result in self.search_results]))

    @robot_alias("click_result_on__name__")
    def click_result(self, i):
        """Click the result, index starting at 1"""

        # Here, "self.results" is a list of result objects, which
        # abstract the DOM structure and functionality of a single
        # Google result listing.

        # i is passed in as string from Robot... so, we
        # cooerse it to an int.
        self.search_results[int(i)-1].go()

        # If we click on a Google result link, we don't know
        # what kind of page it will be, so we return a generic Page.
        return Page()
