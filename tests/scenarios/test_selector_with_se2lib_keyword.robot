*** Settings ***

Documentation  Selectors should work with Se2Lib keywords.
...
Library    Selenium2Library
Library    selectors_page.Page

*** Test Cases ***

Test Widget Site
   Open Widget Page
   Click Element  search-button
   [Teardown]  Close Widget Page