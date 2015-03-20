*** Settings ***
Documentation  Some docs

Library    mypage.MyPage
 
*** Test Cases ***
 
Test 1
    Open MyPage        
    [teardown]  Close MyPage

Test 2
    Open MyPage        
    [teardown]  Close MyPage



