*** Settings ***
Library  keyword_naming.C

*** Test Cases ***
Should Not Have To Specify Page Name When Class Extends Se2Lib Keyword
  Open C
  Footer Text Should Be  I am the footer.
  Input Text  dog
  Search Input Text Should Be  dog
  [Teardown]  Close C