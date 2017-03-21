*** Settings ***
Library  stacktracepage.StackTracePage

*** Test Cases ***
Test Stack
  Open Stack Trace Page
  Raise Division By Zero
  [Teardown]  Close Stack Trace Page