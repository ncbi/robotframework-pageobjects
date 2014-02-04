*** Settings ***

Documentation  An attempt at encapsulating the Pubmed Service
...
Resource  entrez.robot


*** Keywords ***

Find Related Data  [Arguments]  ${value}
    Wait Until Element Is Visible   rdDatabase
    Select From List By Value  rdDatabase  ${value}
    Wait Until Page Contains  NCBI Bookshelf books that cite the current articles.
    Click Button  rdFind

