*** Settings ***
Library  simon_says.MyBasePage
Library  simon_says.SubA
Library  simon_says.SubB

*** Test Cases ***
Should Not Have To Specify Page Name For A Keyword When Two Subclasses Inherit It
  Open Sub A
  Footer Text Should Be  I am the footer.
  Search For  dog
  Footer Text Should Be  I am the footer.
