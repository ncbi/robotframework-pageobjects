call rmdir robot /s /q
call virtualenv robot
call robot\Scripts\activate.bat
call pip install nose
call pip install -e .
call pip install mock
call nosetests -vs --with-xunit tests/test_unit.py tests/test_functional.py
