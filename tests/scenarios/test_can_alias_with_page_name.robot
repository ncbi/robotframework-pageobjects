*** Settings ***
Library  keyword_naming.AliasedMethodPage

*** Test Cases ***
Can Call An Aliased Method Without Page Name
    Open Aliased Method Page
    Do Something
    Close Aliased Method Page
