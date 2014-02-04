*** Settings ***

Documentation  A test of flow from pubmed to Books, showing how we might properly encapsulate the AUT(s)
...
Library    ExposedBrowserSelenium2Library
Library    PubmedPageLibrary
Library    BooksPageLibrary

*** Test Cases ***

Test PubMed To Books
    Open Browser    http://www.ncbi.nlm.nih.gov/pubmed  firefox
    Search Pubmed For  breast cancer
    Find Related Data  books
    Click Books Docsum Item Number  0
    Click Table Of Contents
    [teardown]  Close Browser

*** Keywords ***

