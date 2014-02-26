call rmdir robot /s /q
call virtualenv robot
call robot\Scripts\activate.bat
call pip install nose
call pip install -r requirements.txt
call nosetests -vs --with-xunit tests/
