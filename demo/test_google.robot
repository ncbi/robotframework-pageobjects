*** Settings ***

Documentation  My first IFT tests

...
Library  Selenium2Library
Library  google.GoogleHomePage
Library  google.GoogleSearchResultPage
Library  google.DestinationPage
*** Test Cases ***

When I search Google and click on first result, resulting page's title should contain search term

    Open Google Home Page
    Search For                      cat
    Click Result                    0
    Title Should Contain            cat
    [Teardown]  Close Browser
