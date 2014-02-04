*** Settings ***

Documentation  entrez.robot: An attempt at encapsulating the Pubmed Service
...

Library  ExposedBrowserSelenium2Library

*** Keywords ***

Search For  [Arguments]  ${term}
    Input Text  term  ${term}
    Click Button  search