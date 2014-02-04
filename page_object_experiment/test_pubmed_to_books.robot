*** Settings ***

Documentation  A test of flow from pubmed to Books, showing how we might properly encapsulate the AUT(s)
...
Resource      pubmed.robot

*** Test Cases ***

Test PubMed To Books
    Set Selenium Speed  1
    Open Browser    http://www.ncbi.nlm.nih.gov/pubmed  phantomjs
    Search For  breast cancer
    Find Related Data  books
    Click Docsum Item Number  0
    Title Should Be  Foo
    [teardown]  Close Browser


*** Keywords ***

Title Should Be  [Arguments]  ${expected}
    ${t}  Get Pubmed Title
    Should Be Equal  ${t}  ${expected}
