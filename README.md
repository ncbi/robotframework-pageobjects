# Robot Framework Page Objects

This Python package adds support of the [Page Object](http://martinfowler.com/bliki/PageObject.html) pattern to [Robot Framework](http://robotframework.org/) & Robot Framework's [Selenium2Library](https://github.com/rtomac/robotframework-selenium2library).  

The main point of using page objects is to factor out page implementation details (locators, UI details etc.) from the actual test suites. This makes the tests read more about the services a page offers and what's being tested instead of the internals of the page. It also makes your tests much more maintainable. For example, if a developer changes an element ID, you only need make that change once--in the appropriate page object.

Each page object is simply a Robot library that inherits from this package's base `Page` class. These library classes can work independently of Robot
Framework, even though they ultimately inherit from Robot Framework's Selenium2Library. This  allows you to encapsulate page logic Robot libraries, but use those libraries in any testing framework, including 
Python [unittest](https://docs.python.org/2/library/unittest.html) test cases.


## Installing
TODO

## How it Works

Here's a Robot test case using some page objects written using the `Page` base class. We need to import any page objects libraries we need in our test
case. **Note**: The `Page` class inherits from Selenium2Library, so all methods (keywords) on Selenium2Library are available in your tests, and from `self` from within one of your page objects.

*test_google.robot*:

    *** Settings ***

    Documentation  Tests searching Google and ending up on Apple.
    ...
    Library    google.Page
    Library    google.ResultPage

    *** Test Cases ***

    Test Google To Apple
        Open Google
        Search Google For  Apple Computers
        On Google Result Page Click Result  1
        Title Should Be  Apple
        [Teardown]  Close Google

This shows you can write the same test, using the same page object libraries outside of Robot, using, for example, Python's unittest module:

    import unittest
    import google


    class TestGoogleSearch(unittest.TestCase):

        def setUp(self):
            self.google_page = google.Page().open()

        def test_google_search_to_apple(self):
            result_page = self.google_page.search("apple computers")
            result_page.click_result(1)
            result_page.title_should_be("Apple")

        def tearDown(self):
            self.google_page.close()

    unittest.main()


Now we need an actual Google Robot library to make the test work:

*google.py*:

    from robotpageobjects import Page, robot_alias


    class Page(PageObjectLibrary):

        """
        Base Google Page

        """
        uri = "/"

        # name attribute tells Robot Keywords what name to put
        # after the defined method. So, def foo.. aliases to "Foo Google".
        # If no name is defined, the name will be the name of the page object
        # class, in this case `Page`.
        name = "Google"

        # selectors dictionary is an inheritable dictionary
        # mapping names to Selenium2Library locators.
        selectors = {
            "search input": "xpath=//input[@name='q']", 
            "search button:: "id=gbqfba",
        }

        def search(self, term):
            self.input_text("search input", term)
            self.click_element("search button")
            return ResultPage()

Now we want to code a Google search result page. Here's the Google Result page object:

*google.py*:

    ...
    class ResultPage(Page):

        """
        A Google Result page. Inherits from Google Page.
        """
        # Google uses ajax requests for their searches.
        uri = "/#q=cat"

        name = "Google Result Page"

        def click_result(self, i):
            # Calling resolve_selector fills in the "n" variable in 
            # the selector template at-run-time for the "nth selector link".
            # We need to cast the 'i' method parameter to an 'int' because Robot passes
            # in all keyword parameters as strings.
            locator = self.resolve_selector("nth result link", n=int(i))
     
            # Now, we pass the resolved locator to the inherited click_link method.
            self.click_link(locator)
            return Page()

## Setting Options

### Built-in IFT options

IFT test-runs always require at least the setting of one option external to the test case: `baseurl`. Setting `baseurl` allows the page object to define its `uri` independent of the host. This allows you to easily run your tests on a dev/qa/production host without having to change your page object. You can set a default `baseurl` by setting a `baseurl` property on your page object class. The base `Page` class defines several other built-in options relevant whether using your page objects in Robot or plain, Python tests. These are:

- baseurl: Default is "http://www.ncbi.nlm.nih.gov". The host for any tests you run. This facilitates test portability between different environments instead of hardcoding the test environment into the test.

- browser : Default is phantomjs. Sets the type of browser used. Values can be: firefox, phantomjs (default). Eg: (ift-env) $ pybot -v browser:firefox mytest.robot, or any browser that Sauce Labs supports.

- log_level : Default is "INFO". Sets the logging threshold for what's logged from the log method. Currently you have to set -L or --loglevel in Robot, not -vloglevel:LEVEL. See  and Logging, Reporting & Debugging.
- sauce_apikey : The API key (password) for your [Sauce](http://www.saucelabs.com) account. Never hard-code this in anything, and never commit the repository. If you need to store it somewhere, store it as an environment variable.
- sauce_browserversion : The version of the sauce browser. Defaults to the latest available version for the given browser.
- sauce_device_orientation : Defaults to "portrait". For mobile devices, tells the page object what orientation to run the test in.
- sauce_platform : A platform Sauce Labs supports.
- sauce_username: The user name of your Sauce account. Never hard-code this in anything, and never commit the repository. If you need to store it somewhere, store it as an environment variable.
- selenium_implicit_wait : A global setting that sets the maximum time to wait before raising an ValueError. Default is 10 seconds. For example, for a call to click_element, Selenium will poll the page for the existence of the passed element at an interval of 200 ms until 10 seconds before raising an ElementNotFoundException.
- selenium_speed : The time in seconds between each Selenium API call issued. This should only be used for debugging to slow down your tests so you can see what the browser is doing. Default is 0 seconds. eg. $ pybot -v selenium_speed:1 mytest.robot
- service_args : Additional command-line arguments (such as "--ignore-ssl-errors=yes") to pass to the browser (any browser) when it is run. Arguments are space-separated. Example: PO_SERVICE_ARGS="--ignore-ssl-errors=yes --ssl-protocol=TLSv1" python mytest.py

Once set, these option values are available as attributes on the page object. For example, self.baseurl.

The rest of this page explains the various ways you can set these options, and even ways to pass in arbitrary data.

### Setting options/data with environment variables

#### Setting individual options/data

Both Robot and Python IFT tests support setting options/data via environment variables. For example, you can change the local browser from phantomjs (default) to Firefox by setting the browser option via the PO_BROWSER environment variable:

	$ export PO_BROWSER=firefox

Now when you run your tests, they will be launched in Firefox. Note that the environment variable is the name of the option, prepended with `PO_`, in all upper case. For example, you'd pass the `baseurl` option by setting `PO_BASEURL`.

These options are only set until the next time you log out of your Unix terminal. To make them persist across sessions, put the same export statement in your `~/.bash_profile file`, then source it:

	$ source ~/.bash_profile

#### Setting options/data en masse

For both Robot and non-Robot tests, you can set multiple options by using a variable file. Create a Python module and set variables to the values you want. The values can be resolved however you like, with arbitrary complexity, as long as the variables are accessible at the module level. For example:

in `myvars.py`:

	import getpass

	# Silly example, but shows you can set options intelligently
	if getpass.getuser() == “me”:
    		browser = "firefox"

This would set the browser to Firefox only if the current user is “me”.

Then set the `PO_VAR_FILE` environment variable to the path of the variable file you just created:

	$ export PO_VAR_FILE=/home/cohenaa/projects/ift/myvars.py

Remember, to make the setting persistent you must add this export statement to your ~/.bash_profile file and source it.

### Setting options/data in Robot via pybot and the command-line

In Robot tests, you can also pass in options, like browser, baseurl etc. from the command-line via pybot using the `—variable` or `-v` options. For example, you can set the browser and baseurl like this:

	$ pybot -v browser:firefox -v baseurl:http://mydomain.com mytests/

This is the same as setting `PO_BROWSER` and `PO_BASEURL` as environment variables. You can also set options *en masse* from pybot using the `—variablefile` or `-V` options. Note that setting options/data via pybot overrides the values set as environment variables.

## Robot Keyword Mapping


IFT Page object classes are also Robot libraries, meaning that Page object method names are directly usable as Robot keywords.

By default, a page object method is mapped to two Robot keywords: one without the page object name and one with the page object name appended to the end. Take this page object, for example:

	from robotpageobjects import Page

	class MyPage(Page):
    		uri = "/"

    		def search(self, term):
        	...

The search method maps to both `Search` or `Search My Page` keywords. This lets you be either implicit or explicit about what page you are on in your Robot test.

### Customizing Robot Keywords

IFT gives Page object authors some control over how Page object method names are mapped to Robot keywords:

- You can allow the test writer to insert the page object name at a specific place in the keyword (not just at the end) by using the robot_alias decorator with a `__name__` token. For example:

    from robotpageobjects import Page, robot_alias

    class MyPage(Page):
        uri = "/"

        @robot_alias("search__name__for")
        def search_for(self, term):
            ...

This code would map to both `Search For` or `Search My Page For` keywords.

- If you want to name your page object class something other than the name used in the keywords, use the name attribute on the page object class. For example:

    from robotpageobjects import Page, robot_alias

    class MyPage(Page):
        
        uri = "/"

        name = "mypage"

        def search(self, term):
            ...

Your Robot keywords would then be `Search` or `Search mypage`, regardless of the class name, `MyPage`.

Being implicit or explicit about page object names in your Robot tests is a matter of taste, and depends on how you want your tests to read. In general, you should be explicit about what page you're on when you navigate to a new page. For example:

	Test Search
   	Open My Page
   	Search For  cat
   	My Result Page Should Have Results  20
   	
        

