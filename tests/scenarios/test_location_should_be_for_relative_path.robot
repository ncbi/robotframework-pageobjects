*** Settings ***

Documentation  Tests for Robot Framework Page Object package.
...
Library    Selenium2Library
Library    ncbi.NCBIPage

*** Test Cases ***

Test Widget Site
    Open NCBI Page  path=pubmed
    Location Should Be  /pubmed
    Location Should Be  /med
    [Teardown]  Close NCBI Page