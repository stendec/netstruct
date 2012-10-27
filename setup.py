#!/usr/bin/env python

from distutils.core import setup

with open("README.rst") as file:
    long_description = file.read()

setup(
    name="netstruct",
    version="1.1.1",
    description="Packed binary data for networking.",
    long_description=long_description,
    author="Stendec",
    author_email="me@stendec.me",
    url="https://github.com/stendec/netstruct",
    py_modules = [ "netstruct" ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Internet",
        "Topic :: Software Development",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy"
        ],
    )
