*** Settings ***
Library    GeTRMPageLibrary
Test Template	Test locsearch

*** Keywords ***
Test locsearch	[Arguments]	${term}    ${header_text}
	
	Open Getrm
	Search Getrm    ${term}
	Getrm Result Arrow Should Exist
	Go To Getrm Results
	Getrm Headers Should Match	${header_text}
	Close Getrm

*** Test Cases ***
Term: 1q24		 1q24			Homo sapiens: GRCh37.p\\\d+\\\s+Chr\\\s1\\\s\\\WNC_000001.\\\d+\\\W:\\\s164.7\\\d+M\\\s-\\\s173.6\\\d+M
Term: Neurofibromatosis	 Neurofibromatosis	Homo sapiens: GRCh37.p\\\d+\\\s+Chr\\\s17\\\s\\\WNC_000017.\\\d+\\\W:\\\s29.6\\\d+M\\\s-\\\s29.\\\d+M