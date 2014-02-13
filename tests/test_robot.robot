*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    Selenium2Library
Library    widget.Page
Library    widget.ResultPage

*** Test Cases ***

Test Widget Site
    Open Widget Page
    Search Widget Page For  cool thing
    Widget Search Result Page Should Have Results  3
    [Teardown]  Close Widget Page
