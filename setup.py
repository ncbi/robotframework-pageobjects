#!/usr/bin/env python

import os
from setuptools import setup, find_packages

reqs = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    'requirements.txt')
REQUIRES = filter(None, open(reqs).read().splitlines())
print REQUIRES

setup(
    name="Robot Experiment",
    version="0.1",
    description="Experiments with Robot Framework and IFT", 
    author="National Center for Biotechnology Information",
    install_requires=REQUIRES,
    packages=find_packages(exclude=("tests",)),
    zip_safe=False
)
