*** Settings ***
Library  keyword_naming.SubA
Library  keyword_naming.SubB

*** Test Cases ***
Should Not Have To Specify Page Name For A Keyword When Two Subclasses Inherit It
  Open Sub A
  Footer Text Should Be  I am the footer.
  Search For  dog
  Footer Text Should Be  I am the footer.
  [Teardown]  Close Sub A
