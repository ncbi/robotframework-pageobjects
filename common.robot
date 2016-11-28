*** Settings ***
Library     Selenium2Library
Library     robotpageobjects.Page
Library     uuid

*** Variables ***
${width}    1024
${height}   768
${browser}  chrome

*** Keywords ***
Save Selenium Screenshot
    [documentation]     Make sure there is a unique name to prevent overwriting
    ${screenshot_index}=    Get Variable Value    ${screenshot_index}    ${0}
    Set Global Variable    ${screenshot_index}    ${screenshot_index.__add__(1)}
    ${time}=    Evaluate    str(time.time())    time
    Capture Page Screenshot    selenium-screenshot-${time}-${screenshot_index}.png

Startup
	[documentation]	Initial work to be completed in suite startup
    Register Keyword To Run On Failure      Save Selenium Screenshot
    Open    ${baseurl}
    Set Window Size	${width}    ${height}

Shutdown
	[documentation]	Final record keeping, cleanup
	Capture Page Screenshot     end.png
	Close

