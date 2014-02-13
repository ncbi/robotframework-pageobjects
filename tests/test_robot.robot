*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    Selenium2Library
Library    widget.Page

*** Test Cases ***

Test Widget Site
    Open Widget Page
    [Teardown]  Close Widget Page
