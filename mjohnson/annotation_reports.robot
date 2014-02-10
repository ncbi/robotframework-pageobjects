*** Settings ***
Library	AnnotationReportPageLibrary

*** Test Cases ***

Test Report Open
     ${species}=	Set Variable	Apis_mellifera
     ${build}=          Set Variable	102
     Open AnnotationReport	${species}	${build}
     Assign Id To Element	css=#BuildInfo	H1
     Element Should Contain	H1              ${species}
     Element Should Contain	H1              ${build}
     [Teardown]  Close AnnotationReport
