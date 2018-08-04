#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='pypools',
      version='1.0.2',
      description='Request miners pools',
      author='varga',
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Programming Language :: Python :: 3.4',
                   'Natural Language :: Russian',
                   'Operating System :: POSIX :: Linux'],
      packages=['pypools'],
      install_requires=['systemd', 'json2html', 'configobj',
                        'py-zabbix', 'validictory'],
      python_requires='~=3.4')
