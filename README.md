# Robot Framework Page Objects 

**NOTE**: Though support was never guaranteed, NCBI is no longer able to maintain this project. We've moved
off of Robot Framework due to lack of timely Python3 support in Robot Framework and the fact that the majority of our developers/test-writers prefer to write
tests in Python. You are free to either fork the project to address any issues or to adopt the project.
Please comment on [this issue](https://github.com/ncbi/robotframework-pageobjects/issues/61) if you'd like to adopt it.

## Build
[![Build Status](https://travis-ci.org/ncbi/robotframework-pageobjects.svg?branch=master)](https://travis-ci.org/ncbi/robotframework-pageobjects)

## Installing

    $ pip install robotframework-pageobjects
    
## Compatibility
Currently `Robot Framework Page Objects` is developed and tested on Linux systems only. 
Windows compatibility is unknown and probably broken. Pull requests are welcome.

## Developing
This package is developed by a core group of folks at [NCBI](http://www.ncbi.nlm.nih.gov) for our own use. We figured it might be useful for others so we open-sourced it. We are always willing to look at issues and even address them (sometimes). Please, though, understand that we only have cycles to address those issues that directly impact our testing. Otherwise, we are likely to ask you to fork, try to address the issue yourself, then issue a pull request. We are very willing to help you with that process. Whatever you do, create an issue in github, and we will try our best to answer your questions, address the issue ourself, or ask you to try.

All branches in this repo are tied to the [Travis continuous integration system](https://travis-ci.org/ncbi/robotframework-pageobjects). Whenever we push a branch from our repo the build gets kicked off there and tests are run. When you fork a branch you should run tests locally. To run tests:

1. `$ virtualenv env`
2. `source env/bin/activate`
3. `(env)$ pip install nose`
4. `(env)$ nosetests -vs tests/test_*.py`

Again, please feel free to ask for help.

## What it is 
This Python package adds support for the [Page Object](http://martinfowler.com/bliki/PageObject.html) pattern with [Robot Framework](http://robotframework.org/) and Robot Framework's [Selenium2Library](https://github.com/rtomac/robotframework-selenium2library). Though this
package is a [Robot library](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#extending-robot-framework), it's usable outside the Robot context and facilitates use of the page object pattern independently of any Python testing framework. This means you can use it to create
page objects and run tests in other testing frameworks like  
[`unittest`](http://docs.python.org/2/library/unittest.html), 
[lettuce](http://lettuce.it/tutorial/simple.html) etc. 

In addition to providing a base `Page` class to build upon, this package provides 
many other conveniences apart from page object modeling including:

- A hidden, yet accessible Selenium2 `driver` instance, which allows you to focus
on the *application under test* (AUT) instead of Selenium2 implementation details.
- Easy parameterization, normalization, and setting of testing variables, like the AUT's host,
the browser type to test with, [Sauce Labs](https://saucelabs.com/) integration, timeouts 
for locating injected content after page-load etc. 
- Convenient helper functions like `find_element`, `find_elements` that take [locators](http://rtomac.github.io/robotframework-selenium2library/doc/Selenium2Library.html#Locating%20elements)
*or* [WebElements](http://selenium-python.readthedocs.org/en/latest/api.html#module-selenium.webdriver.remote.webelement) as parameters.
- Built-in and readable *assertion methods* on the page object. For example `location_should_be`, `title_should_be` etc.
- Much more...

Like we said, the package is very flexible: it doesn't force you to use Robot, nor forces you
to do heavy page object modeling up front. This is great for convicing your organization to move toward
BDD and page object development because you can approach those ideals iteratively. Even
with light modeling, and use of a non-BDD framework, your test suites
can still benefit from the above listed features. 

## Some Examples
Here's some examples of about the simplest Robot test case you could write using this package. You don't even have
to model a page object...you could just write a test using the base `Page` class that comes with this package, yet by
simply using `Page` you get some things for free, like the ability to:

- pass in test options such as `baseurl`, `browser` etc. to both Robot tests and Python tests (see [Setting Options](#setting-options) for more
built-in options you can use)
- use of Selenium2Library keywords/methods in both Robot and Python tests 

This is a very simple Robot test using `Page`:

    *** Settings *** 
    Library  robotpageobjects.Page

    *** Test Cases *** 
    Can Open Google
        Open
        Location Should Be  http://www.google.com/
        Close


To run it:

    $ pybot -vbaseurl:http://www.google.com test.robot 
    ==============================================================================
    Test                                                                          
    ==============================================================================
    Can Open Google                                                       | PASS |
    ------------------------------------------------------------------------------
    Test                                                                  | PASS |
    1 critical test, 1 passed, 0 failed
    1 test total, 1 passed, 0 failed
    ==============================================================================

By default, the test runs in PhantomJS, but you could run it in Firefox (if it's set up locally)
like this:

    $ pybot -vbaseurl:http://www.google.com -vbrowser:firefox test.robot

Now the same test in Python:

    import unittest
    from robotpageobjects import Page


    class MyTestCase(unittest.TestCase):
        def test_can_open_google(self):
            p = Page()
            p.open()
            p.location_should_be("http://www.google.com/")
            p.close()

    if __name__ == "__main__":
        unittest.main()

To run, set the baseurl option with an environment variable:

    $ export PO_BASEURL=http://www.google.com
    $ python test.py
    .
    ----------------------------------------------------------------------
    Ran 1 test in 1.411s

    OK

To run with Firefox, use the `PO_BROWSER` environment variable:

    $ export PO_BROWSER=firefox
    $ python test.py


## More on page objects
Though you could write very simple tests using this package, it allows you to heavily model your applications-under-test using
your own subclasses of `Page`. You can factor out page implementation details (element locators, UI details etc.) from the actual test suites. This makes the tests read more about the services a page offers and what's being tested instead of the internals of the page. It also makes your tests much more maintainable. For example, if a developer changes an element ID, you only need make that change once--in the appropriate page object.

## How it works
Each page object you create is simply an object that inherits from this package's base `Page` class. In the context of a Robot test, the object is a Robot library. Since these classes are *plain old Python classes* they can work independently of Robot
Framework, even though they ultimately inherit their base methods from Robot Framework's Selenium2Library. This  allows you to encapsulate page logic in Robot libraries, but still leverage those classes in any testing framework if need be. Thus the brunt
of your coding can go in the page objects, not the test suites. Your tests become more declarative, deferring the work
to the page objects. Since the page objects are written in Python you are less tied to a particular testing framework, though of
course we are partial to Robot! 

## Demo

To see some more complex page objects, Check out and run the [demo](https://github.com/ncbi/robotframework-pageobjects/tree/master/demo). 

## How the demo works

Here's a Robot test case using some page objects written using the `Page` base class. We need to import any page objects libraries we need in our test
case. **Note**: The `Page` class inherits from Selenium2Library, so all methods (keywords) in Selenium2Library are available in your tests, and from `self` from within one of your page objects.

*test_pubmed.txt*:

    *** Settings ***
    Documentation  My first IFT tests
    ...
    Library  pubmed.PubmedHomePage 
    Library  pubmed.PubmedDocsumPage 
    Library  pubmed.PubmedArticlePage
        
    *** Test Cases ***
    When a user searches Pubmed for a term, the first result page's body should contain the search term
        Open Pubmed
        Search For  cat
        Click Result On Pubmed Docsum Page  1
        Pubmed Article Page Body Should Contain  cat
        [Teardown]  Close Pubmed Article Page 

This shows you can write the same test, using the same page object libraries outside of Robot, using, for example, Python's unittest module. *test_google.py*:

    from pubmed import PubmedHomePage
    import unittest


    class PubmedTestCase(unittest.TestCase):

        def setUp(self):
            self.pubmed_homepage = PubmedHomePage()
            self.pubmed_homepage.open()

        def test_first_result_page_body_should_contain_search_term(self):
            pubmed_docsum_page = self.pubmed_homepage.search_for("cat")
            self.article_page = pubmed_docsum_page.click_result(1)
            self.article_page.body_should_contain("cat")

        def tearDown(self):
            self.article_page.close()

    if __name__ == "__main__":
        unittest.main()

Now we need an actual pubmed page objects to make the test work:

*pubmed.py*:

    from robotpageobjects import Page, robot_alias
    from robot.utils import asserts


    class PubmedHomePage(Page):
        """ Models the Pubmed home page at:
            HOST://ncbi.nlm.nih.gov/pubmed"""

        name = "Pubmed"
        uri = "/pubmed"

        selectors = {
            "search input": "id=term",
            "search button": "id=search",
        }


        @robot_alias("type_in__name__search_box")
        def type_in_search_box(self, txt):
            self.input_text("search input", txt)
            return self

        @robot_alias("click__name__search_button")
        def click_search_button(self):
            self.click_button("search button")
            return PubmedDocsumPage()

        @robot_alias("search__name__for")
        def search_for(self, term):
            self.type_in_search_box(term)
            return self.click_search_button()


    class PubmedDocsumPage(Page):
        """Models a Pubmed search result page. For example:
        http://www.ncbi.nlm.nih.gov/pubmed?term=cat """

        uri = "/pubmed/?term={term}"

        selectors = {
            "nth result link": "xpath=(//div[@class='rslt'])[{n}]/p/a",
        }

        @robot_alias("click_result_on__name__")
        def click_result(self, i):
            locator = self.resolve_selector("nth result link", n=int(i))
            self.click_link(locator)
            return PubmedArticlePage()

    class PubmedArticlePage(Page):

        uri = "/pubmed/{article_id}"

        @robot_alias("__name__body_should_contain")
        def body_should_contain(self, str, ignore_case=True):
            ref_str = str.lower() if ignore_case else str
            ref_str = ref_str.encode("utf-8")
            body_txt = self.get_text("css=body").encode("utf-8").lower()
            asserts.assert_true(ref_str in body_txt, "body text does not contain %s" %ref_str)
            return self


**Note**: You must return *something* from public (non-underscored) page object methods: either a value from a getter method or a page object instance from non-getter methods. Remember, when you navigate to a new page by clicking a link, submitting a form etc. you should return the appropriate page object. 

The rest of this README explains many more details around writing page objects and putting them to work in tests.

## Setting Options

### Built-in options for `Page`

Test-runs always require at least the setting of one option external to the test case: `baseurl`. Setting `baseurl` allows the page object to define its `uri` independent of the host. This allows you to easily run your tests on a dev/qa/production host without having to change your page object.  The base `Page` class defines several other built-in options relevant whether using your page objects in Robot or plain, Python tests. **Note**: Sauce option values
like `sauce_platform` etc. can be gotten from Sauce's [configuration app](https://docs.saucelabs.com/reference/platforms-configurator/?_ga=1.167969697.126382613.1414715829#/). The bult-in options are:

- `baseurl`: The host for any tests you run. This facilitates test portability between different environments instead of hardcoding the test environment into the test.

- `browser` : Default is phantomjs. Sets the type of browser used. Values can be: firefox, phantomjs (default). Eg: (ift-env) $ pybot -v browser:firefox mytest.robot, or any browser that Sauce Labs supports.

- `log_level` : Default is "INFO". Sets the logging threshold for what's logged from the log method. Currently you have to set -L or --loglevel in Robot, not -vloglevel:LEVEL. See  and Logging, Reporting & Debugging.
- `sauce_apikey` : The API key (password) for your [Sauce](http://www.saucelabs.com) account. Never hard-code this in anything, and never commit the repository. If you need to store it somewhere, store it as an environment variable.
- `sauce_browserversion` : The version of the sauce browser. Defaults to the latest available version for the given browser.
- `sauce_device_orientation` : Defaults to "portrait". For mobile devices, tells the page object what orientation to run the test in.
- `sauce_platform` : A platform Sauce Labs supports.
- 'sauce_screenresolution' : This controls the screen resolution used during the saucelabs test. See https://docs.saucelabs.com/reference/test-configuration/#specifying-the-screen-resolution for the limitations on the screen resolutions per OS.
- `sauce_username`: The user name of your Sauce account. Never hard-code this in anything, and never commit the repository. If you need to store it somewhere, store it as an environment variable.
- `selenium_implicit_wait` : A global setting that sets the maximum time to wait before raising an ValueError. Default is 10 seconds. For example, for a call to click_element, Selenium will poll the page for the existence of the passed element at an interval of 200 ms until 10 seconds before raising an ElementNotFoundException.
- `selenium_speed` : The time in seconds between each Selenium API call issued. This should only be used for debugging to slow down your tests so you can see what the browser is doing. Default is 0 seconds. eg. $ pybot -v selenium_speed:1 mytest.robot
- `service_args` : Additional command-line arguments (such as "--ignore-ssl-errors=yes") to pass to the browser (any browser) when it is run. Arguments are space-separated. Example: PO_SERVICE_ARGS="--ignore-ssl-errors=yes --ssl-protocol=TLSv1" python mytest.py

Once set, these option values are available as attributes on the page object. For example, self.baseurl.

The rest of this page explains the various ways you can set these options, and even ways to pass in arbitrary data.

### Setting options/data with environment variables

Both Robot and Python tests using page objects support setting options/data via environment variables. For example, you can change the local browser from phantomjs (default) to Firefox by setting the browser option via the PO_BROWSER environment variable:

	$ export PO_BROWSER=firefox

Now when you run your tests, they will be launched in Firefox. Note that the environment variable is the name of the option, prepended with `PO_`, in all upper case. For example, you'd pass the `baseurl` option by setting `PO_BASEURL`.

These options are only set until the next time you log out of your Unix terminal. To make them persist across sessions, put the same export statement in your `~/.bash_profile file`, then source it:

	$ source ~/.bash_profile

### Setting options/data with a variable file

For both Robot and non-Robot tests, you can set multiple options by using a variable file. Create a Python module and set variables to the values you want. The values can be resolved however you like, with arbitrary complexity, as long as the variables are accessible at the module level. For example:

in `myvars.py`:

	import getpass

	# Silly example, but shows you can set options intelligently
	if getpass.getuser() == “me”:
    		browser = "firefox"

This would set the browser to Firefox only if the current user is “me”.

Then set the `PO_VAR_FILE` environment variable to the path of the variable file you just created:

	$ export PO_VAR_FILE=/path/to/myvars.py

Remember, to make the setting persistent you must add this export statement to your ~/.bash_profile file and source it.

### Setting options/data in Robot with the pybot command-line

In Robot tests, you can also pass in options, like browser, baseurl etc. from the command-line via pybot using the `—variable` or `-v` options. For example, you can set the browser and baseurl like this:

	$ pybot -v browser:firefox -v baseurl:http://mydomain.com mytests/

This is the same as setting `PO_BROWSER` and `PO_BASEURL` as environment variables. You can also set options *en masse* from pybot using the `—variablefile` or `-V` options. Note that setting options/data via pybot overrides the values set as environment variables.

### Setting options/data in the Page Object class

Options can also be set in the Page Object class implementation by creating a class-level dict variable `options`.

in `pubmed.py`:

     class PubmedHomePage(Page):

         options = {
             'baseurl': 'http://www.ncbi.nlm.nih.gov',
         }

## Robot Keyword Mapping


Page object classes are also Robot libraries, meaning that Page object method names are directly usable as Robot keywords.

By default, a page object method is mapped to two Robot keywords: one without the page object name and one with the page object name appended to the end. Take this page object, for example:

	from robotpageobjects import Page

	class MyPage(Page):
    		uri = "/"

    		def search(self, term):
        	...

The search method maps to both `Search` or `Search My Page` keywords. This lets you be either implicit or explicit about what page you are on in your Robot test.

### Customizing Robot Keywords

`robotframework-pageobjects` gives Page object authors some control over how Page object method names are mapped to Robot keywords:

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

A singular page object models a page with only one URL. For example, `GoogleHomePage` is singular, because there's only one URI: “/“. Singular page objects should have a `uri` attribute (defaults to '/') in their class definitions:

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

To understand how to find and interact with elements using page objects, it's important to understand `Selenium2Library` (Se2Lib)--a third-party library allowing Robot Framework tests to drive Selenium2. Se2Lib exposes a lot of [useful keywords](http://robotframework-seleniumlibrary.googlecode.com/hg/doc/SeleniumLibrary.html?r=2.5) that are essentially Selenium helper methods. Many of these keywords, such as  `Click Element` (`click_element`) , `Double Click Element` ( `double_click_element` ) etc. deal with interacting with web page elements. They hide some of the complexity of dealing with the underlying Selenium2 Python bindings.

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
    class MyPage(Page):
    
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

- Maintainability/inheritablility. Locators are defined once in the selector dictionary, 
instead of embedded throughout your test-code. When a developer changes the page structure, you know where to go to make your tests pass again. Selectors are inherited from parent page object classes. The dictionaries are merged, so common elements need only be defined in the parent class.
- Readability. Instead of referring to a hard-to-read locator, you can name the locator something meaningful and then 
refer to it by name throughout your code.

#### Passing selectors to Se2Lib methods

Note in the above example the page object methods pass selectors instead of locators to Se2Lib methods, 
like `click_button`. This is possible because `Page` has overridden Se2Lib's underlying method for finding elements. 

This means you can pass selectors instead of locators to all Se2Lib methods that accept locators

- for maintainability and readability, you should pass selectors to Se2Lib methods, not locators.
- if you write your own helper methods for finding or interacting with elements allow them to be passed 
locators *and* selectors.
- You can also pass an instance of a selenium WebElement to Se2Lib methods instead of a selector or locator

Here is an example of a Robot test using a selector defined in a page object:

    class MyPage(NCBIPage):
        uri = "/somewhere"
	  
        selectors = {
	    "first name": "css=#myform input[name=firstname]",
	    "last name": "css=#myform input[name=lastname]",
	    "form submit": "css=#myform input[type=submit]"
	}
					   
    ....
			    
    *** Settings ***
    Library  MyPage
					     
    *** Test Cases ***
    Form Should Submit
        [Setup]  Open My Page
	Input Text  first name  Fleagle
        Input Text  last name  Smith
        Click Element  form submit
	Page Should Contain  Thank you. Your form was submitted.
	[Teardown]  Close


#### Looking up elements from the end of a list

It can be helpful to look up elements from the end of a list. It especially helps when the number of elements is 
large or variable. You can verify the content of the last row with a negative index, i.e. -1, as you would in a Python list:

    ...
    
    class MyPage(Page):
    
        selectors = {
            "long-table": "#long_table_id"
            ...
        }
    
        long_table_should_contain_last_row(self, expected_row):
            # Verifies the content in the last row (i.e. row -1) of "long table"
            locator = self.resolve_selector("long-table")
            self.table_row_should_contain(locator, "-1", expected_row)
            return self

The second-to-last element in a list has index -2, and so on.

Support for negative indexes has been added for the following built-in Robot keywords:

    - Table Row Should Contain
    - Table Column Should Contain
    - Table Cell Should Contain

At the time of this writing, these table-related keywords are the only ones that support negative indexes.

#### Selector templates

Sometimes you want to find elements, but part of the locator is variable. In this case we use selector templates. To 
do so, define a selector, surrounding the variable part of the locator with brackets `{`,  `}`.

In your page object method that uses the selector template, call `resolve_selector`, 
passing in the selector name followed by keyword arguments matching the variable names in your selector template. This method returns the expanded locator, which you can then pass to any methods that accept locators/selectors to find or interact with page elements.

For instance, let's say you want to select the nth item in some list on a particular page. Here's how we'd do it:

    ...
    
    class MyPage(Page):
    
        selectors = {
            "nth result link": "xpath=id('product-list')/li/a[{n}]",
            ...
        }
    
        def click_result_link(self, index=0):
            """ Click the nth product result link """
            # Robot passes in parameters as strings, so we need to cast it to an int.
            xpath_index = int(index) + 1
             
            # "n" keyword maps to the variable name in the selector template.
            locator = self.resolve_selector("nth result link", n=xpath_index)
            self.click_link(locator)
            return ProductPage()

#### Self-Referential Selectors

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

### Using WebElements

`Page` is based on Selenium/Selenium2Library which uses the `WebElement` class to model DOM nodes. Most often, 
we don't actually need a reference to the WebElement because all page objects give us many convenience methods like 
`click_element`, `click_button`, input_text etc. All these methods are on the base `Page` object, 
so from within your page object you can call them on `self`.

If, for some reason, you need a direct reference to a WebElement you can get it by passing a locator/selector to 
`find_element` or `find_elements`,  which is also on every page object.  You can then use this reference when 
invoking Se2Lib keywords instead of a locator/selector.  When at all possible, however, 
work at the Selenium2Library level, not at the WebElement level. For example:

    ...
    class MyPage(Page):
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

### Waiting

#### Sleeping

Just don't. Sometimes page content, including text or elements are inserted into the DOM after page-load. Or sometimes Selenium2 will drive the browser so fast that we can't be sure when the page has loaded. If you try to find or operate on these page elements you'll get either get a ValueError or Selenium's NoSuchElementException. Don't fall into the trap of calling time.sleep(). Why?

- your tests will be brittle: the content could be available after the time you slept for. Sometimes your tests 
will pass and sometimes they will fail with errors. Inconsistent tests are almost as bad as no tests.
- your tests will be slow. For example, your content could be available in 1/8 of a second. If you sleep for one 
second you are stalling your tests for 7/8 of a second for no reason. This can start to add up over the course of several tests.

#### Implicitly waiting

The solution is waiting, not sleeping. The idea is to repeatedly poll the page for the element's existance and then sleep 
at much smaller increments–up to some maximum (`Page` sets this maximum timeout to 10 seconds). By default page object 
methods that take selectors or locators as parameters to find or operate on elements will poll the page until they find the element they are supposed to find or operate on. These methods include:

- `find_element`
- `find_elements`
- `click_element`
- `click_button`
- `get_text`
- `input_text`
- etc.

This means that when calling these types of methods, you generally don't have to worry about whether the element exists at the time of the 
method call. `Page` will wait approximately as long as it takes for the element to show up in the DOM before raising a 
`ValueError`. One issue with this is that method calls that fail to find elements will take 10 seconds to raise a 
ValueError. See the Explicitly waiting section on how to deal with this situation.

To globally change the implicit wait timeout (default is 10 seconds), set the `selenium_implicit_wait` option. 

The implicit wait does not apply to an element's visibility. It only applies to existance in the DOM. It's possible for an element to exist in the DOM, but not be visible, and Selenium will not allow you to interact with an element that's not visible. For this you may need wait_until_element_is_visible .
Explicitly waiting

There are cases where you'd like to specify exactly how long you want to wait for an element's existence without 
setting the global selenium_implicit_wait option. There are several ways to do this:

    - Call find_element with the optional wait keyword parameter. This overrides the default 10 second implicit wait 
    timeout, but only for the one call to find_element. Currently you cannot pass a wait parameter to any of the other element finding/manipulating Se2Library methods, such as click_element, input_text etc. See . After finding the element, you'll then have to drop down to the Selenium layer. For example:

    class MyPage(Page):
        ...
        def do_something(self):
            el = self.find_element("some selector", wait=2)
            el.click()
    ...

    - Call Se2Lib methods like wait_until_page_contains_element , passing an explicit wait parameter

#### Waiting for arbitrary conditions

Sometimes you need to wait for something more complex than just an element. In this case use 
Selenium2Library's `wait_for` or  
`wait_for_condition`. You'll have to pass these functions callbacks that check some condition and return a Boolean. 
`Page` will poll the page every 500 milliseconds for the condition to become `True`, then it will continue to the next 
line of code. Here's an example:

    class MyPage(Page):
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

If you need to pass a callback a parameter, you'll have to pass a lambda to `wait_for`.

#### Overriding parent selectors

If you want to redefine a selector defined in a parent class, use the `Override` class:

    ...
    from robotpageobjects.page import Override
    
    
    class MyPage(Page):
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
        
    
## Making Assertions
 
Asserting conditions is the basis of automated testing. Here's a very simple example from a basic Python unit test Test Case:

    from unittest import TestCase
    
    class AdditionTestCase(TestCase):
        def test_add(self):
            self.assertEquals(1 + 1, 2)

...and here's a simple assertion in Robot Framework (OK, Robot's not great for math..):

    *** Settings ***
     
    Documentation  Simple assertion.
     
    ...
    Library    Builtin
    
    *** Test Cases ***
    
    Test One Plus One
        Should Be Equals As Numbers  Evaluate  ${1] + ${1}  2

When you write automated tests using page objects, you assert more complex things, such as the number of results in a
 search result page, for example.

Although we stress separating page behavior in page objects from test code,  we think it's better to write thin 
wrappers for assertions as methods on your page objects, instead of writing assertions in your tests. 
The advantage to writing assertions as page object methods is that they are reusable and tend to make the tests more readable. 

For example, compare these two Robot tests:

    *** Settings ***
     
    Documentation  Tests for Pubmed Docsum pages
     
    ...
    Library    pubmedpageobjects.PubmedHomepage
    Library    pubmedpageobjects.PubmedDocsumPage
    Library    Builtin
     
    *** Test Cases ***
     
    Test Pubmed Search Returns 20 Results
        Open Pubmed Homepage
        Search Pubmed Homepage for  breast cancer
        Pubmed Docsum Page Results Should Be  20
        ${NUM_RESULTS}  Get Results From Pubmed Docsum Page
        Should Be Equal As Numbers  ${NUM_RESULTS}  20
        [Teardown]  Close Pubmed Docsum Page

...see how that assertion looks like code? Once we start assigning variables and making assertions using Robot's built in "Should" assertion keywords, we lose the flow and readability of the test. Remember our goal is to make the test look like a simple list of instructions that a tester could easily run manually. Compare that to this:

    *** Settings ***
     
    Documentation  Tests for Pubmed Docsum pages
     
    ...
    Library    pubmedpageobjects.PubmedHomepage
    Library    pubmedpageobjects.PubmedDocsumPage
     
    *** Test Cases ***
     
    Test Pubmed Search Returns 20 Results
        Open Pubmed Homepage
        Search Pubmed Homepage for  breast cancer
        Pubmed Docsum Page Results Should Be  20
        [Teardown]  Close Pubmed Docsum Page

...now that the Pubmed Docsum page has its own results_should_be assertion method, the test is more English-like, and that assertion can be reused by another tester.

The method, `results_should_be()`, would look like this:

    ...
    from robot.utils import asserts
    
    class PubmedDocsumPage(EntrezDocsumPage):
        """
        Example page object, the real
        PubmedDocsumPage may not have these methods
        """
       
        @robot_alias("__name__results_should_be")
        def results_should_be(self, expected_num=20):
            
            # This method does the work of getting the actual docsums
            # and doesn't change the state of the page. It simply queries 
            # the page for existing state.
            docsums = self._get_docsums()
    
            # Here's the actual assertion, using Robot's assertions.
            asserts.assert_equals(len(docsums), expected_num)
            

Make sure your assertion methods are thin wrappers for assertions. Their signatures should include the word "should", 
which follows the example of Robot assertions and makes it obvious that the method is asserting a condition.

Page object assertion methods shouldn't change the state of the page (eg. clicking links, navigating back etc.) and minimal computation, looping etc. State change and computation should be done in page object action/helper methods. In your test, 
you should get the page to the state where you want it to be using other page object methods, and call the assert method.

## Sauce Labs Cloud Testing Service Integration

robotframework-pageobjects integrates seamlessly with
[Sauce Labs](http://saucelabs.com/), a cloud service allowing you to run Selenium-based
jobs on a [multitude of browsers and platforms](https://docs.saucelabs.com/reference/platforms-configurator/#/).  
To use Sauce:

1. Make sure you have an account with a valid username, API key and web login. 
1. Set the `sauce_apikey`, `sauce_username`, and the `sauce_platform` options. 
1. Set the `browser` option to a browser other than phantomjs.

See the Built-in options section [above](#built-in-options-for-page) for options
related to running tests in Sauce. 

## Logging Reporting & Debugging

### Robot

#### Default Logging & Reporting

By default, Robot outputs logs, HTML reports and XML. The XML is not "xunit XML", so CI systems like TeamCity can't parse results out-of-the-box. 
Luckily, you can pass the  -x flag to pybot to produce XML that Teamcity can parse.

You can also turn off all default reporting. Run pybot -h on the command line to see all of Robot's default logging and reporting options.
Logging from page objects

When working in Robot, you can log arbitrary data from  page objects by calling the page object's `log` method, 
which is defined in the base `Page` object. By default calls to log are logged at the `INFO` log level. The log 
message is written to the log.html file generated by Robot Framework and to `stdout`.  Calling log from page objects 
in Robot is useful because Robot intercepts `stdout`, so you can't simply call print from your page objects to debug. 

To turn off printing to `stdout` call `log` with the `is_console` parameter set to False. Here are some example calls
 to log. The example assumes the log level is set to `INFO` or less:

    ...
    class MyPage(Page):
    
        def some_keyword(self):
            self.log("First message") # this logs to log.html and to stdout at the INFO level
            self.log("logging some message", is_console=False) # This logs to just log.html at the INFO level
            self.log("logging yet again", level="DEBUG") # This logs as DEBUG to log.html and to stdout

To filter out what log messages are reported set the `-L` or `--loglevel` option to your desired threshhold. For 
example, if you log to the `INFO` level but set the threshold to `CRITICAL` with the `--loglevel option`, 
your `INFO` log messages to log.html will be filtered out.

### Reporting from test runs

In Robot, the default report, written to report.html should be sufficient for human-readable results of a test-run. You can always use XSLT to transform output.xml or xunit output to generate  a custom report. If this still doesn't suffice, you can use Robot's listener interface. This provides hooks into Robot's test life-cycle which allows you to do any kind of custom reporting or actions you want.

Remember that TeamCity can parse xunit output within a run-configuration, so there's no need to do anything apart from generating xunit output and adjusting your build configuration to get TeamCity working with  output.  In TeamCity, add the "XML report processing" build feature under your run configuration and choose "Ant Junit" as the report type.
Debugging Robot runs

You can use the log method to log debug messages to console or to output.xml or log.html. If you are getting an error and want to see the 
Python trace back, set the logging level to TRACE using the --loglevel or -L options from pybot:

(myapp) $ pybot -L TRACE test_foo.robot

This will give you an accurate stack trace in your log.

### Outside Robot

#### Default logging & reporting

If you write  tests without the Robot layer, you are responsible for your own logging and reporting–that's one of the many advantages of 
using Robot. unittest offers default test runner and result classes. In fact, the results you see on the screen when you run a unittest suite is actually using TextTestRunner ,  but you can write your own runner and result classes if you need to.  You can also check out nose. It's a framework built on top of unittest and has more robust test discovery and reporting options, including xunit output.

##### Logging

Just like in Robot, you can log from page objects by calling the page object's `log` method, 
which is defined in the base `Page` object. By default log writes at the "INFO" log level to `stdout` and to a file 
called `po_log.txt`. You can set the global logging threshold by setting the `PO_LOG_LEVEL` environment variable or the 
log_level variable in a variable file. The available logging levels can be found here.

### pdb (Built-In Python Debugger)

`pdb` is available from within the Robot layer or without it.  Simply use it like you would in any other python 
application by importing pdb and then using pdb.set_trace():

    ...
    class MyPage(Page):
    
        def some_keyword(self):
            self.click_element("some element")
            import pdb
            pdb.set_trace()
            

## Page Components
            
### How Components Work

Components encapsulate discrete parts of a page and make them reusable across multiple page objects and page object packages. 
Components also help to keep base page classes uncluttered with functionality not necessarily needed by every derived class.

For example, a site's Global Header would make a good component because it may be on many of a site's pages, 
but not all. It has its own particular DOM structure and functionality, independent from the page it's on. 
We could code the global header functionality in the site's base page object. That would give every page object 
access to its properties and methods, but that would also bloat every page object class with code that might not be 
needed.

Instead, we could write a `GlobalHeaderComponent`. The `GlobalHeaderComponent` is a class encapsulating  everything the  Global Header has and can do.

Let's take a look at how this all works. 

    from robotpageobjects import Component


    class GlobalHeaderComponent(Component):
        """ Encapsulates the common, 
        GlobalHeader found on most NCBI pages.
        """

    	# All selectors are implicitly found relative to
        # the "reference WebElement" for
        # this component. This assures that you are finding
        # the element for **this** component.
        # If for some reason, you need to access the actual
        # reference WebElement for this instance, 
        # access: self.reference_webelement from a component method.
        # In the case of the header, all elements are contained
        # within a single, parent element, so selectors describe
        # elements found inside the reference element.
        selectors = {
            "Search Database Select": "id=database",
            "Search Term Input": "id=term",
            "Search Button": "id=search",
        }

        # As a rule, allow easy access
        # as properties, instead of getter
        # methods. This ain't Java.
        @property
        def database_selected(self):
            # Remember, try to use Selenium2Library methods, instead of
            # the lower level WebDriver API. You can pass selectors to
            # these as well as locators.
            return self.get_value("Search Database Select")

        def search(self, db, term):
            self.select_from_list_by_value("Search Database Select", db)
            self.input_text("Search Term Input", term)
    		self.click_button("Search Button")
            # Let the page object return the correct page object
            # after calling this method on the GlobalHeader instance.
            # we won't actually code that here...

Next, the page object defines a dictionary indicating what components it uses. Each key of the dictionary is a component's class, 
and the corresponding value is the locator used by the page to find instances of the component. The page object then 
automatically creates properties on itself corresponding to the name of the component class. This allows 
the page object author to access the component's properties and methods from within page object methods. 

The test author shouldn't directly access the component, rather page object methods should wrap component properties and methods. 
Here's the page class using the component. Note here that the properties `globalheader` and `globalheaders` are 
automatically created and attached to the page object. These properties are determined from the class name 
`GlobalHeaderComponent`. `globalheader` is a reference to a single `GlobalHeaderComponent` instance (for use on pages 
like this, where there is only one global header), and `globalheaders` is a list of all GlobalHeaderComponent 
instances on the page (in this case there is only one).

Note also that, as with selectors, any components you define in a super class of your page are inherited by your page and merged with any 
components you define in your components dictionary.

    from ncbipageobjects import NCBIPage
    from robotpageobjects import robot_alias
    from .global_header_component import GlobalHeaderComponent
    from robot.libraries.BuiltIn import BuiltIn

    class MyAppHomePage(NCBIPage):
    	components = {GlobalHeaderComponent: "id=universal_header"}

        @robot_alias("selected_database_in_global_header_should_be_on__name__")
        def selected_database_in_global_header_should_be(self, db):
            BuiltIn.should_be(self.globalheader.selected_database, db)

        @robot_alias("search_from_global_header_on__name__for")
        def search_from_global_header(self, db, term):
            self.globalheader.search(db, term)
            # Here we'd have to figure out what page object to return…
            # but we won't bother with that logic here…

Now your Robot (or other kinds of) tests can use the component, but only indirectly via page object methods. 

*test_my_page.robot*:

    *** Settings ***
    Documentation  Tests for My Page.
    ...
    Library    myapppageobjects.MyAppHomePage

    *** Test Cases ***
    Test Header On My App
        Open Browser  My App Home Page
        Selected Database In Global Header Should Be  All Databases
        Search In Global Header For  dog
        etc.
        [Teardown]  Close My App Home Page

### Return Values from Component Methods

Methods on component classes should not return page objects. They can, of course, return anything else. 
Let the page object method that accesses the component decide whether it needs to return: either itself or another 
page object instance.

### Sub Components

Components can use other components. The parent component should define its components in a dictionary, just as page objects do. 
This way the parent component can access instances of the sub component using `self`. Let's say, for example, 
that a header component has an advanced search section that's implemented using a show/hide toggler JavaScript widget:

    from robotpageobjects import Component
    from ncbipageobjects.jig import TogglerComponent
    
    
    class  HeaderComponent(Component):
    
        components = {TogglerComponent: "css=.jig-ncbitoggler"}
    
        ...
        def open_advanced_search_section(self):
            try:
                advanced_toggler = self.togglers[0]
            except KeyError:
                raise Exception("No advanced search section found in the header")
    
            advanced_toggler.open()

### Finding Component Instances with No DOM Hook

Sometimes there's no way to find instances of a component on a page because there's no ID or classes on the reference element. 
Ideally, you should have the developer put an ID or classes in the HTML source or on the DOM. If that's not feasible, use the 
Selenium2Library's DOM strategy instead of xpath or css as your locator strategy. This way you can execute arbitrary 
JavaScript to find the components on the page. Here's an example:

    from robotpageobjects import Page, Component, ComponentManager
     
    class InPageNavComponent(Component):
        …
     
    class Mypage(Page):
        components = {InPageNavComponent: "dom=Query('body > div').filter(function(){return typeof jQuery(this).data('ncbiinpagenav') !== 'undefined';})"}
