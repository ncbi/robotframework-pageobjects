from robotpageobjects import Page, robot_alias
from robot.utils import asserts

from googleresultcomponent import GoogleResultComponentManager
class GoogleHomePage(Page):

    uri = "/"
    name = "Google"

    # Google makes it hard to 
    # get elements by ID or class etc.
    # They do this in order to make it
    # hard to do screen scaping.
    # So here we use fairly brittle
    # xpaths. Instead, try to get your
    # devs to put IDs and/or classes
    # so you can use id or css strategies,
    # eg: "id=myid", "css=.myclass" 
    selectors = {
        "search box": "xpath=//input[@name='q']",

        # The search button is marked up differently depending on the user-agent.
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
        return GoogleResultPage()

class GoogleResultPage(Page, GoogleResultComponentManager):

    uri_template = "#q={q}"

    @robot_alias("all_result_titles_on__name__should_contain")
    def all_results_should_contain(self, expected_text):
        """Asserts that all google result titles have specified text
        :param text: The expected text"""

        # This wait won't be necessary after resolving https://jira.ncbi.nlm.nih.gov/browse/QAR-47914
        self.wait_until_page_contains_element(GoogleResultComponentManager.locator)
        asserts.assert_true(all([expected_text in result.text.lower() for result in self.results]))

    @robot_alias("click_result_on__name__")
    def click_result(self, i):
        """Click the result, index starting at 1"""
        # i is passed in as string from Robot...
        self.results[int(i)-1].go()
        return Page()
