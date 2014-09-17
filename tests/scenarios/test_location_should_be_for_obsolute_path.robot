*** Settings ***
Documentation     Tests for Robot Framework Page Object package.
Library           Selenium2Library
Library           po.ncbi.NCBIPage

*** Test Cases ***
Test Widget Site
    Open NCBI Page    path=pubmed
    Location Should Be    http://qa.ncbi.nlm.nih.gov/pubmed
    [Teardown]    Close NCBI Page
