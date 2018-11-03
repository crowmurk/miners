#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import pyminers

setuptools.setup(
    name='pyminers',
    version=pyminers.__version__,
    author=pyminers.__author__,
    description='Request miners',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 3.4',
                 'Natural Language :: Russian',
                 'Operating System :: POSIX :: Linux'],
    packages=setuptools.find_packages(),
    test_suite='pyminers.tests',
    install_requires=['systemd', 'json2html', 'configobj',
                      'py-zabbix', 'validictory'],
    python_requires='~=3.4',
)
