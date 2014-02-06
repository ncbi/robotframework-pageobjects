Robot Page Objects API
======================

This is a demo of the Robot Page Object API.

Why?
----

- Robot is great, but it would be nice to encapsulate page/application logic using standard Python OO techniques
without losing the readability inherent in typical Robot Framework test cases.
- It would also be great if we could reuse these Robot page objects in generic unittests

Example
----

Here's a Robot test case using some page objects. We need to import the ExposedBrowserSelenium2Library and any page
libraries we are going to use in our test case. This imports in each library's keywords.

By default, any keywords defined in the page object take the name of the page object class (minus "PageLibrary") and append
it to the end of the keyword. This makes the test cases more readable.

But there are times we need more flexibility in mapping the way keywords are defined in the page object to the
keyword used in the Test Case. In this case, you will need to use the "robot_alias" annotation to replace a the special
"__name__" delimiter with the name of the page object.


Here are some examples:

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

