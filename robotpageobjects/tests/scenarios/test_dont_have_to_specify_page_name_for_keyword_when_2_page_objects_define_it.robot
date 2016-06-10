*** Settings ***
Library  keyword_naming.A
Library  keyword_naming.B

*** Test Cases ***
Should Not Have To Specify Page Name For A Keyword When Two Classes Define It
  Open A
  Footer Text Should Be  I am the footer.
  Search For  dog
  Footer Text Should Be  I am the footer.
  [Teardown]  Close A
