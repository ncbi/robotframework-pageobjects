Robot Framework/Selenium2Library Page Objects
=============================================

Adds the concept of Page Objects to Robot Framework & Selenium2Library. Page objects can work independently of Robot
Framework allowing you to encapsulate page logic in Robot Framework testcases or outsides of Robot Framework (eg.
Python unittest test cases).


First Things First
------------------

Take a look at:

- [Robot Framework's Quick Start Guide](http://robotframework.googlecode.com/hg/doc/quickstart/quickstart.html) to get an idea of what Robot Framework is
- [Selenium2Library](http://rtomac.github.io/robotframework-selenium2library/doc/Selenium2Library.html)
to learn how Robot Framework can drive Selenium2.
- [Page Object Pattern](http://martinfowler.com/bliki/PageObject.html)

How it Works
------------

Here's a Robot test case using some page objects. We need to import any page objects libraries we need in our test
case. **Note**: If we want to use standard Selenium2Library keywords, we need to also include Selenium2Library. This
code is in demos/test_google_search_to_apple.robot:

    *** Settings ***

    Documentation  Tests searching Google and ending up on Apple.
    ...
    Library    Selenium2Library
    Library    pageobjects.google.Page
    Library    pageobjects.google.ResultPage

    *** Test Cases ***

    Test Google To Apple
        Open Google
        Search Google For  Apple Computers
        On Google Result Page Click Result  1
        Title Should Be  Apple
        [Teardown]  Close Google

Here's a regular, unittest test case using the same page object. This code is in demos/test_google_search_to_apple.py:

    import unittest
    from pageobjects import google


    class TestGoogleSearch(unittest.TestCase):

        def setUp(self):
            self.google_page = google.Page().open()

        def test_google_search_to_apple(self):
            result_page = self.google_page.search("apple computers")
            result_page.click_result(1)

            # This call to .se will go away when we import
            # se methods into the page object.
            result_page.se.title_should_be("Apple")

        def tearDown(self):
            self.google_page.close()

    unittest.main()


Here is the Google page object. It is designed to be the base class of all Google page objects and is in pageobjects
/google.py:

    from pageobjects.base.PageObjectLibrary import PageObjectLibrary, robot_alias


    class Page(PageObjectLibrary):

        """
        Base Google Page

        For example, search() works on any google page.
        """
        homepage = "http://www.google.com"

        # name attribute tells Robot Keywords what name to put
        # after the defined method. So, def foo.. aliases to "Foo Google".
        # If no name is defined, the name will be the name of the page object
        # class.
        name = "Google"

        # By default, page object methods
        # map in Robot Framework to method name + class name.
        # Eg. Search Google  term. But we can use robot_alias decorator
        # with the __name__ token to map the page object name to
        # wherever you want in the method. So this would become
        # Search Google For  term.
        @robot_alias("search__name__for")
        def search(self, term):
            self.se.input_text("xpath=//input[@name='q']", term)
            self.se.click_element("gs_htif0")
            return ResultPage()

Here's the Google Result page object. It's also in pageobjects/google.py:

    ...
    class ResultPage(Page):

        """
        A Google Result page. Inherits from Google Page.
        """
        name = "Google Result Page"

        # This will become "On Google Result Page Click Result"
        @robot_alias("on__name__click_result")
        def click_result(self, i):
            els = self.se._element_find("xpath=//h3[@class='r']/a[not(ancestor::table)]", False, False, tag="a")
            try:
                els[int(i)].click()
            except IndexError:
                raise Exception("No result found")

