SHELL := /bin/bash
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

all: test

test:
	@echo "Run Tests"
	nosetests -vs --with-xunit robotpageobjects/tests/test_unit.py robotpageobjects/tests/test_functional.py
