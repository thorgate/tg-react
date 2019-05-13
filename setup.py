#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "dummy_settings"

import tg_react

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = tg_react.__version__

readme = open('README.rst').read()

setup(
    name='tg-react',
    version=version,
    description="""Helpers for react based applications running on django.""",
    long_description=readme,
    author='Thorgate',
    author_email='jyrno@thorgate.eu',
    url='https://github.com/thorgate/tg-react',
    packages=[
        'tg_react',
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.8,!=2.1.0,!=2.1.1,!=2.1.2,!=2.1.3,!=2.1.4,!=2.1.5,<3.0',
    ],
    license="BSD",
    zip_safe=False,
    keywords='tg-react',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
