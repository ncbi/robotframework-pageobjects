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
   	

## Opening Page Objects, Page Object URLs & Navigation

Page objects have an open method (inherited from the base `Page` object) that opens the browser to the appropriate URL for that object. Page Objects always take the hostname as a required parameter to the test run via the `baseurl` option to avoid coupling environments to the tests. 

There are two types of page objects: singular and templated.

### Singular Page Objects

A singular page object models a page with only one URL. For example, `GoogleHomePage` is singular, because there's only one URI: “/“. Singular page objects should have a `uri` attribute in their class definitions:

	...
	class MyAppHomePage(EntrezPage):
    		uri = "/myapp"
		…

A tester using your page object instance will open it with no parameters:

Robot:

	...
	Open Google Home Page
	...

Python:

	>>> from google import GoogleHomePage
	>>> hp = GoogleHomePage()
	>>> hp.open()

### Templated Page Objects

A templated page object models a page with many (perhaps infinite) possible URIs. Templated page objects use curly braces in their `uri` attribute to denote where parts of the URI may vary. For example:

	...
	class PubmedArticlePage(object):
		“”” Models a page like http://www.ncbi.nlm.nih.gov/pubmed/25362170
		where the number is an article ID:
		uri = "/{article_id}"
    		....

You then open a templated page object like this:

Robot:

	...
	Open Pubmed Article Page article_id=24587471
	...

Python:

	>>> from pubmed import PubmedArticlePage
	>>> article_page = PubmedArticlePage()
	>>> article_page.open({"article_id": "24587471"})

The values of the template variables are saved in a dictionary in the Page Object after the page is opened if you need to reference them later.  For example:

	>>> item_page.uri_vars['article_id']
	"24587471"

### Opening a page directly to a URL

Let's say you want to go to a particular URL that your page object models, but the URL doesn't conform to your page object's `uri` attribute, such as a hash or query string. You might just have one test that does this, and you do not want to modify the page object to add the hash or query string. In this case, you can simply pass in a string instead of template arguments.

In Robot:

	...
	Open My App Item Page  /myapp/1234?report=full
	...

In Python:

	>>> item_page = MyAppItemPage()
	>>> item_page.open("/myapp/1234?report=full")

This is good for one-off cases. In general, for query strings, you should model different views of the same page as separate page object classes inheriting from a base class


## Finding & Interacting with page elements

### Understanding Selenium2Library keywords/methods

To understand how to find and interact with elements using page objects, it's important to understand `Selenium2Library` (Se2Lib)--a third-party library allowing Robot Framework tests to drive Selenium2. Se2Lib exposes a lot of useful keywords that are essentially Selenium helper methods. Many of these keywords, such as  `Click Element` (`click_element`) , `Double Click Element` ( `double_click_element` ) etc. deal with interacting with web page elements. They hide some of the complexity of dealing with the underlying Selenium2 Python bindings.

At the functional test layer, we try to avoid these kinds of lower-level calls (both to Se2Lib and to Selenium2) because tests should focus on what a page can or can't do, not on its implementation details. It so happens that Se2Lib is flexible enough to be used outside the context of Robot Framework, so its methods can be safely used within page objects, whether those page objects are used in Robot tests or regular Python `unittest` test cases.

This package’s `Page` object inherits from Selenium2Library, so your page objects get to use all these methods out-of-the-box. 

Remember, before you code your own "helper" method for a page object, check to see that an appropriate Se2Lib method doesn't already exist. When you inherit from `Page` you can find these methods on `self`.

### Locators vs. selectors

A locator is an Se2Lib concept. Locators are strings that tell Selenium how to find an element. It's of the form `strategy=value` where strategy can be:

- id
- xpath
- css
- link (link text)
- jquery/sizzle
- dom (arbitrary JavaScript)

For example:

- `id=foo`
- `xpath=id('foo')//a[@class='bar’]`
- `css=#foo a.bar`
- `dom=getElementsByTagName(“a”)[1]`

A selector, on the other hand, is a Robot Page Object concept. It's a named locator. You define selectors on your page object class and/or component class as a Python dictionary. Your page object class will inherit any super classes' selectors, and any subclass of your page object will inherit your selectors. So, make sure your selector isn't already defined in a super class. If it isn't, make sure it's specific to type of page you're modeling. If it's more generic, it may belong in a super class.


### Selectors in action

Here's an example of using selectors in your page object:

...
class MyPage(NCBIPage):

    ...
    selectors = {
        "search button": "id=srcbtn",
        "search textfield": "css=".s",
    }

    def enter_search_term(self, term):
        self.input_text("search textfield", term)

    def click_search_button(self):
        self.click_button("search button")
        return SearchResultPage()

	def search(self, term):
        self.enter_search_term(term)
        return self.click_search_button()

Using selectors is less brittle than locators. Selctors give you:

    Maintainability/inheritablility. Locators are defined once in the selector dictionary, instead of embedded throughout your test-code. When a developer changes the page structure, you know where to go to make your tests pass again. Selectors are inherited from parent page object classes. The dictionaries are merged, so common elements need only be defined in the parent class.
    Readability. Instead of referring to a hard-to-read locator, you can name the locator something meaningful and then refer to it by name throughout your code.

Passing selectors to Se2Lib methods

Note in the above example the page object methods pass selectors to Se2Lib methods, like click_button, instead of locators. This is possible because IFT has overridden Se2Lib's underlying method for finding elements. This means:

    you can pass selectors instead of locators to all Se2Lib methods that accept locators
    for maintainability and readability, you should pass selectors to Se2Lib methods, not locators.
    if you write your own helper methods for finding or interacting with elements:
        allow them to be passed selectors
        if they are applicable to any web page, issue a pull request for the base Page object: https://stash.ncbi.nlm.nih.gov/projects/IFT/repos/robotframework-pageobjects/browse/robotpageobjects/page.py

Looking up elements from the end of a list

It can be helpful to look up elements from the end of a list.  It especially helps when the number of elements is large or variable.

For example, say you have a table with many rows, ending with these three rows:
AL672294.10	HYcos-53	HSCHR1_CTG32_1	SC	fin	Excellent	2,000	0	100	
AL845371.2	HYcos-64	HSCHR1_CTG32_1	SC	fin	Excellent	2,000	0	100	
AL672183.3	HYcos-35	HSCHR1_CTG32_1	SC	fin	Minor problem	908	0	99.339	identity < 99.6%; alignment length < 2000

You can verify the content of the last row with a negative index, i.e. -1, as you would in a Python list:

...

class MyPage(Page):

	selectors = {
		"long-table": "#long_table_id"
		...
	}

	@robot_alias("my_long_table_should_should_contain_last_row")
	long_table_should_contain_last_row(self, expected_row):
        # Verifies the content in the last row (i.e. row -1) of "long table"
        locator = self.resolve_selector("long-table")
        self.table_row_should_contain(locator, "-1", expected_row)
		return self

The second-to-last element in a list has index -2, and so on.

Support for negative indexes has been added for the following built-in Robot keywords:

    Table Row Should Contain
    Table Column Should Contain
    Table Cell Should Contain

At the time of this writing, these table-related keywords are the only ones that support negative indexes.
Selector templates

Sometimes you want to find elements, but part of the locator is variable. In this case we use selector templates.

    Define a selector, surrounding the variable part of the locator with brackets ("{ }")
    In your page object method that uses the selector template, call resolve_selector, passing in the selector name followed by keyword arguments matching the variable names in your selector template. This method returns the expanded locator, which you can then pass to any methods that accept locators/selectors to find or interact with page elements.

For instance, let's say you want to select the nth item in some list on a particular page. Here's how we'd do it:

...

class MyPage(Page):

    selectors = {
        "nth result link": "xpath=id('product-list')/li/a[{n}]",
        ...
    }

    @robot_alias("click_result_link_on__name__")
    def click_result_link(self, index=0):
        """ Click the nth product result link """
        xpath_index = index + 1
         
        # "n" keyword maps to the variable name in the selector template.
        locator = self.resolve_selector("nth result link", n=xpath_index)
        self.click_link(locator)
        return ProductPage()

Self-Referential Selectors

You can also keep your selectors DRY (Don't Repeat Yourself) by referencing other selectors using python string formatting syntax:

...

class MyPage(Page):

    selectors = {
        "search form": "xpath=//form",
        "form label": "%(search form)s/label",
        ...
    }

    def check_form_label(self):
        """ Make sure the form label is visible """
        self.element_should_be_visible("form label")
        return self()

Using WebElements

IFT is based on Selenium/Selenium2Library which uses the WebElement class to model DOM nodes. Most often, we don't actually need a reference to the WebElement because all page objects give us many convenience methods like click_element, click_button, input_text etc. All these methods are on the base Page object, so from within your page object you can call them on self. See each page object's API docs or Selenium2Library's keyword documentation for more.

If, for some reason, you need a direct reference to a WebElement you can get it by passing a locator/selector to IFT's find_element(s), which is also on every page object. When at all possible, however, work at the IFT level, not at the WebElement level. For example:

...
class MyPage(NCBIPage):
    ...
	selectors = {
        "search button": "id=srcb",
    }

    def click_search_button(self):
        # Don't do:
        # search_btn = self.find_element("search button")
        # search_btn.click()
        # Instead, simply:
        self.click_button("search button")

Waiting
Sleeping

Just don't. Sometimes page content, including text or elements are inserted into the DOM after page-load. Or sometimes IFT will drive the browser so fast that we can't be sure when the page has loaded. If you try to find or operate on these page elements you'll get either get a ValueError or Selenium's NoSuchElementException. Don't fall into the trap of calling time.sleep(). Why?

    your tests will be brittle: the content could be available after the time you slept for. Sometimes your tests will pass and sometimes they will fail with errors. Inconsistent tests are almost as bad as no tests.
    your tests will be slow. For example, your content could be available in 1/8 of a second. If you sleep for one second you are stalling your tests for 7/8 of a second for no reason. This can start to add up over the course of several tests.

Implicitly waiting

The solution is waiting, not sleeping. The idea is to repeatedly poll the page for the element's existance and then sleep at much smaller increments–up to some maximum (IFT sets this maximum timeout to 10 seconds). By default page object methods that take selectors or locators as parameters to find or operate on elements will poll the page until they find the element they are supposed to find or operate on. These methods include:

    find_element
    find_elements
    click_element
    click_button
    get_text
    input_text
    etc.

This means that when calling these types of methods, you generally don't have to worry about whether the element exists at the time of the method call. IFT will wait approximately as long as it takes for the element to show up in the DOM before raising a ValueError. One issue with this is that method calls that fail to find elements will take 10 seconds to raise a ValueError. See the Explicitly waiting section on how to deal with this situation.

To globally change the implicit wait timeout (default is 10 seconds), set IFT's selenium_implicit_wait option. See Setting IFT options & data.

IFT's implicit wait does not apply to an element's visibility. It only applies to existance in the DOM. It's possible for an element to exist in the DOM, but not be visible, and Selenium will not allow you to interact with an element that's not visible. For this you may need wait_until_element_is_visible .
Explicitly waiting

There are cases where you'd like to specify exactly how long you want to wait for an element's existance without setting the global selenium_implicit_wait option. There are several ways to do this:

    Call find_element with the optional wait keyword parameter. This overrides the default 10 second implicit wait timeout, but only for the one call to find_element. Currently you cannot pass a wait parameter to any of the other element finding/manipulating Se2Library methods, such as click_element, input_text etc. See . After finding the element, you'll then have to drop down to the Selenium layer. For example:

    class MyPage(NCBIPage):
        ...
        def do_something(self):
            el = self.find_element("some selector", wait=2)
            el.click()
    ...

    Call Se2Lib methods like wait_until_page_contains_element , passing an explicit wait parameter

Waiting for arbitrary conditions

Sometimes you need to wait for something more complex than just an element. In this case use wait_for or  wait_for_condition. You'll have to pass these functions callbacks that check some condition and return a Boolean. IFT will poll the page every 500 milliseconds for the condition to become True, then it will continue to the next line of code. Here's an example:

class MyPage(NCBIPage):
    ...
    def do_something(self):

		def all_columns_contain_human():
            # some logic that checks that a specific table column
            # contains the text "human"
            ...

        self.wait_for(all_columns_contain_human)
        # Once the condition is True, continue to do something here
        ...
...

If you need to pass a callback a parameter, you'll have to pass a  lambda to wait_for.

Overriding parent selectors

If you want to redefine a selector defined in a parent class, use the Override class:

...
from robotpageobjects.page import Override


class MyPage(NCBIPage):
   ...
    selectors = {
        "search": "id=search-btn",
        "term input": "id=search-input"
    }

class MySpecialPage(MyPage):
    ...

    selectors = {
        Override("search"): "id=my-search-btn"
    }






