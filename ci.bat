call rmdir robot /s /q
call virtualenv robot
call robot\Scripts\activate.bat
call pip install nose
call pip install -e .
call pip install mock
call tasklist /v | find "phantomjs"
call tasklist /v | find "firefox"
call nosetests -vs --with-xunit tests/
