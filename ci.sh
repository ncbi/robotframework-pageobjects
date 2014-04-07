#!/bin/bash

# Script to install a fresh
# virtul env, install robot framework page object and run the branch's tests.
#
# The script outputs an XML file to the checkout directory, which
# contains test results. This can be parsed by CI if needed.
#
# Argument is git branch name.
#
# Script is suitable for use by a CI system.

function main {

    rm -rf robot
    echo "Removing dir"
    rm -rf robotframework-pageobjects
    find . -name *.pyc -exec rm {} \;

    if [ $# -lt 1 ]; then
        echo "Must supply a git branch, aborting..."
        return 1
    fi

    branch=$1

    # Switch to specified branch
    echo "branch:"
    echo $branch
    if [ $? -ne 0 ]; then
        echo "$branch is not a valid git branch, aborting..."
        return 1
    fi

    # Install the virtual env
    virtualenv -p /opt/python-2.7/bin/python2.7 robot
    if [ $? -ne 0 ]; then
        echo "installing virtual env failed, aborting..."
        return 1
    fi

    source robot/bin/activate

    # Need nose to run tests.
    pip install nose

    # Install pageobjects  in the current directory.
    pip install -e .
    if [ $? -ne 0 ]; then
        echo "Install failed, aborting..."
    fi

    # Run tests 
    #nosetests -vs --with-xunit tests/test_unit.py tests/test_functional.py
    ps aux | grep -i phantom
    pybot --variable=baseurl:file://`pwd`/tests/scenarios -P `pwd`/tests/scenarios/po `pwd`/tests/scenarios/test_template_passed.robot
}

main $1
