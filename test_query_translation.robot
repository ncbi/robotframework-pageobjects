*** Settings ***

Documentation  A test suite testing Entrez query translations
...
Library       EntrezLibrary

*** Test Cases ***

Test Entrez Search Details
    Open Pubmed With  phantomjs
    Search For  dog
    Click See More Search Details
    Search Details Should Be  "dogs"[MeSH Terms] OR "dogs"[All Fields] OR "dog"[All Fields]
    [teardown]  Close Browser
