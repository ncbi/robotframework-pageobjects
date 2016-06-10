*** Settings ***
Library  keyword_naming.DoesNotReturnPage

*** Test Cases ***
Every Page Object Method Should Return A Page Object
  Open Does Not Return Page
  Footer Text Should Be  I am the footer.
  [Teardown]  Close Does Not Return Page