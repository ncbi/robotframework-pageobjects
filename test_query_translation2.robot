*** Settings ***
Documentation     Example test cases using the data-driven testing approach.
...
...               Tests use the Search Keyword as the template to the data in the test cases section.

Test Template     Search
Resource          common_resource.robot

*** Keywords ***
Search
    [Arguments]    ${query}    ${expected}
    Open Browser To PubMed Home Page
    Search PubMed For  ${query}
    Click See More Search Details
    Search Details Should Be  ${expected}
    [teardown]  Close Browser

*** Test Cases ***  Query	Expected
QA-1715: by itself, translates as author name   all mm  all mm[Author]
IDX-177 QA-1715: with term lipman translates to [All Fields]), author stop word should be ignored in translation    lipman all mm   lipman[All Fields]
Author Stop Word IDX-177 QA-1715: with author name 'lipman (translates to [Author]), author stop word should be ignored in translation  lipman d all mm	lipman d[Author] OR lipman d[Investigator]

