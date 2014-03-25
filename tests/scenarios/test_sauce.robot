*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    Selenium2Library
Library    ncbi.NCBIPage

*** Test Cases ***

Test Widget Site
    Open NCBI Page  path=pubmed
    Title Should Be  Home - PubMed - NCBI
    Title Should Be  foo
    [Teardown]  Close NCBI Page
