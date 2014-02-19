*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...

Library    widget_no_homepage.Page
Library    widget_no_homepage.SearchResultPage

*** Variables ***

*** Test Cases ***

Test Widget Site
    ${ABS_URL} =   Get Variable Value  ${ABS_URL}
    Open Widget Page  ${ABS_URL}
    Search Widget Page For  cool thing
    Widget Search Result Page Should Have Results  3
    [Teardown]  Close Widget Page
