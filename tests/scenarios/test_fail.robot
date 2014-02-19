*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    widget_abs_homepage.Page
Library    widget_abs_homepage.SearchResultPage

*** Test Cases ***

Test Widget Site
    Open Widget Page
    Search Widget Page For  cool thing

    # This will fail the assertion
    Widget Search Result Page Should Have Results  2
    [Teardown]  Close Widget Page
