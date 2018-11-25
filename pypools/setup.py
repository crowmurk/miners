#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools
import pypools

setuptools.setup(
    name='pypools',
    version=pypools.__version__,
    author=pypools.__author__,
    description='Request miners pools',
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Programming Language :: Python :: 3.4',
                 'Natural Language :: Russian',
                 'Operating System :: POSIX :: Linux'],
    packages=setuptools.find_packages(),
    install_requires=['systemd', 'json2html', 'configobj',
                      'py-zabbix', 'validictory'],
    python_requires='~=3.4',
)
