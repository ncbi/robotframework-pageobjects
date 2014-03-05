::call deactivate
::call pip freeze
call rmdir robot /s /q
call virtualenv robot
call robot\Scripts\activate.bat
call pip freeze
call pip install nose
call pip install -e .
call pip install mock
call python -c "import mock"
::call nosetests -vs --with-xunit tests/
