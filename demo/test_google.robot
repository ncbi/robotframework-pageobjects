*** Settings ***

Documentation  Google Tests

...
Library    demo.GoogleHomePage
Library    demo.GoogleSearchResultPage
Library    robotpageobjects.Page

*** Test Cases ***

When a user searches for a term all results on the result page should contain the search term
    Open Google
    Search Google For  cat
    All Result Titles On Google Search Result Page Should Contain  cat
    [Teardown]  Close Google Search Result Page

When a user searches for a term and the user clicks the first result, the resulting page should contain the term    Open Google
    Open Google
    Search For  cat
    Click Result On Google Search Result Page  1
    Page Should Contain  cat
    [Teardown]  Close Page


