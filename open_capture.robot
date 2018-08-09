*** Settings ***
Resource    common.robot
Suite Setup     Startup
Suite Teardown      Shutdown
Force Tags      quickstart

*** Test Cases ***
Sample Test
    ${links}=    Get Web Elements   css=a
    :FOR    ${some link}    IN  @{links}
    \   Log     ${some link.get_attribute('href')}