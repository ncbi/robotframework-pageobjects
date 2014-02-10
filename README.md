Robot Framework/Selenium2Library Page Objects
==================

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

Example
----

Here's a Robot test case using some page objects. We need to import any page objects libraries we need in our test
case. *Note*: If we want to use standard Selenium2Library keywords, we need to also include Selenium2Library.

Here's how it works:

- By default, any keywords defined in the page object class are aliased to the same keyword name,
but with the name of the page object (minus "PageLibrary"). This means that when using the page object in Robot,
"my_keyword" becomes "My Keyword PageObjectName". This enforces readability and consistency in your Robot Framework
test cases.

- When importing the page object in a unittest TestCase there is no aliasing because the keyword will be predicated
by the instance. This is typical object-oriented and should be inherently readable (at least for code).

- There's an affordance for when you don't want the page object name to be appended to the keyword in Robot Framework
. In this case you define your keyword with the "robot_alias" decorator from the PageObjectLibrary. This allows you
to use a delimiter, "__name__" to tell Robot Framework where to substitute in the page object name.

Here are some examples. Notice how, in general, the name of the page object comes at the end of each keyword. And
notice how readable both examples are. The core logic and Selenium code is all encapsulated in the page objects,
in both the Robot Framework example and the unittest example.

    # testcase.robot

     *** Settings ***

    Documentation  A test of flow from pubmed to Books, showing how we might properly encapsulate the AUT(s)
    ...
    Library    ExposedBrowserSelenium2Library
    Library    PubmedPageLibrary
    Library    BooksPageLibrary

    *** Test Cases ***

    Test PubMed To Books
        Open Pubmed
        Search Pubmed  breast cancer
        Find Related Data From Pubmed In  books
        Click Books Docsum Item  0
        Click Table Of Contents Books
        [teardown]  Close Browser

Here is the same test in a Python unittest TestCase, totally apart from Robot Framework. Notice how here we use the
object's original methods, and it's still readable because they are predicated by the page object instance:

    # testcase.py
    import unittest
    from PubmedPageLibrary import PubmedPageLibrary

    class TestPubmedflows(unittest.TestCase):

        def test_pubmed_to_books(self):
            pubmed_page = PubmedPageLibrary().open()
            pubmed_page.search("breast cancer")
            books_page = pubmed_page.find_related_data_in("books")
            books_page.click_docsum_item(0)
            books_page.click_table_of_contents()
            books_page.close()


Check out this directory for the source code of the PageObject base class and some example page objects which use
PageObjectLibrary.

