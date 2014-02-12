*** Settings ***

Documentation  Tests searching Google and ending up on Apple.
...
Library    Selenium2Library
Library    pageobjects.google.Page
Library    pageobjects.google.ResultPage

*** Test Cases ***

Test Google To Apple
    Open Google
    Search Google For  Apple Computers
    On Google Result Page Click Result  1
    Title Should Be  Apple
    [Teardown]  Close Google