*** Settings ***
Library  simon_says.DoesNotReturnPage

*** Test Cases ***
Every Page Object Method Should Return A Page Object
  Open Does Not Return Page
  Footer Text Should Be  I am the footer.