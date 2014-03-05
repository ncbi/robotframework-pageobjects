call pip freeze
::call rmdir robot /s /q
::call virtualenv robot
::call robot\Scripts\activate.bat
::call pip install nose
::call pip install -e .
::call nosetests -vs --with-xunit tests/
