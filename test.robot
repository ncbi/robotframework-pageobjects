
*** Settings ***
Documentation  Some docs

Library    mypage.MyPage
Library    myotherpage.MyOtherPage
 
*** Test Cases ***
 
When I call 'Say Something', something is said
    Open MyPage
    [teardown]  Close MyPage

When I blah blah, something happens
    Open MyPage
    [teardown]  Close MyPage