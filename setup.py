from __future__ import unicode_literals, print_function
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), 'rb') \
        .read().decode('utf-8')


setup(
    name='multinosetests',
    version='0.1.0',
    author='Miroslav Shubernetskiy',
    description='Helper utility to run multiple nosetests suites. '
                'Useful for makefile scripts.',
    long_description=read('README.rst'),
    url='http://10.134.8.70/E003134/multinosetests',
    packages=find_packages(exclude=['test', 'test.*']),
    scripts=['bin/multinosetests'],
    install_requires=[
        'blessings',
        'six',
    ],
    keywords=' '.join([
        'test',
        'nosetests',
        'nose',
        'nosetest',
    ]),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
)
