call git branch
call rmdir robot /s /q
call virtualenv robot
call robot\Scripts\activate.bat
call pip freeze
call pip install nose
call pip install -e .
call pip install mock
call nosetests -vs --with-xunit tests/
