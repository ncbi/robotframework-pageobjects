*** Settings ***

Documentation  A test suite testing Entrez query translations
...
Resource       common_resource.robot


*** Test Cases ***

Test Entrez Search Details
    Open Browser To PubMed Home Page
    Search PubMed For  dog
    Click See More Search Details
    Search Details Should Be  "dogs"[MeSH Terms] OR "dogs"[All Fields] OR "dog"[All Fields]
    To Stdout  yaya
    Close Browser
