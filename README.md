# Robot Framework Page Objects

This Python package adds support of the [Page Object](http://martinfowler.com/bliki/PageObject.html) pattern to [Robot Framework](http://robotframework.org/) & Robot Framework's [Selenium2Library](https://github.com/rtomac/robotframework-selenium2library). 

Page objects inheriting from this package's base `Page` class can work independently of Robot
Framework allowing you to encapsulate page logic in Robot Framework testcases or outsides of Robot Framework (eg.
Python [unittest](https://docs.python.org/2/library/unittest.html) test cases).


## Background

Take a look at:

- [Robot Framework's Quick Start Guide](http://robotframework.googlecode.com/hg/doc/quickstart/quickstart.html) to get an idea of what Robot Framework is
- [Selenium2Library](http://rtomac.github.io/robotframework-selenium2library/doc/Selenium2Library.html)
to learn how Robot Framework can drive Selenium2.
- [Page Object Pattern](http://martinfowler.com/bliki/PageObject.html)

## How it Works

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
            self.input_text("xpath=//input[@name='q']", term)
            self.click_element("gs_htif0")
            return ResultPage()

Here's the Google Result page object. It's also in `pageobjects/google.py`:

    ...
    class ResultPage(Page):

        """
        A Google Result page. Inherits from Google Page.
        """
        name = "Google Result Page"

        # This will become "On Google Result Page Click Result"
        @robot_alias("on__name__click_result")
        def click_result(self, i):
            els = self.find_elements("xpath=//h3[@class='r']/a[not(ancestor::table)]", required=False, tag="a")
            try:
                els[int(i)].click()
            except IndexError:
                raise Exception("No result found")


### Setting Options

We need to be able to set options for page objects in both the Robot Framework context and outside that context,
such as which browser to use to open the page, and the baseurl to use (in order to easily switch executation between
environments).


#### In Robot

For page objects being used in Robot Framework, follow the Robot standard,
which is to use [variables](http://robotframework.googlecode.com/hg/doc/userguide/RobotFrameworkUserGuide.html?r=2.8.4#creating-variables)
either on the command line or using a variable file:

    $ pybot --variable=browser:firefox --variable=baseurl:http://www.example.com mytest.robot

The `--variable` option must come right after pybot.

or

    $ pybot --variablefile=/path/to/vars.py mytest.robot

The `--variablefile` option is a path to a python module which defines variables in the module's namespace.
Variables can set as complexly as you want, as long as they are in the module's namespace. Keep in
mind that variables set on the command-line override those in the variable file.

#### Outside Robot

Outside of Robot, use environment variables to set options (unittest frameworks like unittest are not really designed
with changable configuration in mind, so it's hard to pass options on the command-line without coupling it to a
particular runner). All environment variables must be uppercase and prefixed with "PO_":

You can set individual options:

    $ export PO_BROWSER=firefox

or you can set options in a variable file, like in Robot:

    $ export PO_VAR_FILE=path/to/vars.py

Individual "PO_" environment variables override any set in a variable file.

### Options Defined by Page Objects

- `baseurl` (PO_BASEURL): which URL to base open calls with. For example if you set your page object's homepage with
self
.homepage
to a relative URL, like "/search", you can set your baseurl to "http://www.example.com". A call to your page object's
 open method will open at "http://www.example.com/search".
- `browser` (PO_BROWSER): which browser to use. Defaults to "phantomjs".
- `loglevel` (PO_LOGLEVEL): decides what level to log. Default is `INFO`. Other levels are, `DEBUG`,
`CRITICAL` etc. Robot logs to its log file, which you can view at log.html.  When using page objects outside of the
Robot context, a log file will be written to the current working directory named po_log.txt. To do your own logging,
from your page object class, do self._log("foo", "bar"). Each parameter sent to `_log()` will get written to the log
as a tab delimited line.
- `selenium_speed` (PO_SELENIIM_SPEED): The speed between Selenium commands. Use this to slow down the page actions,
 which is useful when, for example, it takes a few moments for something to load via AJAX.
