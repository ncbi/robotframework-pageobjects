*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    widget_rel_uri_attr.Page
Library    widget_rel_uri_attr.SearchResultPage

*** Test Cases ***

Test Widget Site
    Open Widget Page
    Search Widget Page For  cool thing

    # This will fail the assertion
    Widget Search Result Page Should Have Results  2
    [Teardown]  Close Widget Page
