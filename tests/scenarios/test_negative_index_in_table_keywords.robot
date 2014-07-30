*** Settings ***

Documentation  Tests negative indexes in Robot keywords, QAR-48165.
...
Library    widget_template.WidgetItemPage
# Keep SE2Lib imported AFTER page object, since we are testing this.
Library    Selenium2Library


*** Test Cases ***

Test negative index for CSS strategy in 'Table Row Should Contain'
    Open Widget Item Page	category=home-and-garden	id=123
    Table Row Should Contain	other-widgets	-1	Useful widget Cube $0.10
    [Teardown]  Close Widget Item Page

Test negative index for XPath strategy in 'Table Row Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Row Should Contain	xpath=//*[@id='see-also']	-1	Moo Thingamajigs 2.5 stars
    [Teardown]  Close Widget Item Page
    	
Test negative index for CSS strategy in 'Table Column Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Column Should Contain	other-widgets	-2	Cube
	[Teardown]  Close Widget Item Page
	
Test negative index for XPath strategy in 'Table Column Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Column Should Contain	xpath=//*[@id='other-widgets']	-2	Cube
	[Teardown]  Close Widget Item Page

Test control for 'Table Cell Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Cell Should Contain	xpath=//*[@id='see-also']	2	2	Gizmos
	[Teardown]  Close Widget Item Page
	
Test negative index for XPath strategy in 'Table Cell Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Cell Should Contain	see-also	-1	-2	Thingamajigs
	[Teardown]  Close Widget Item Page
	
Test negative index for CSS strategy in 'Table Cell Should Contain'
	Open Widget Item Page	category=home-and-garden	id=123
	Table Cell Should Contain	xpath=//*[@id='see-also']	-1	-2	Thingamajigs
	[Teardown]  Close Widget Item Page