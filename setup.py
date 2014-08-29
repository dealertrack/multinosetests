from __future__ import unicode_literals, print_function
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), 'rb') \
        .read().decode('utf-8')


authors = read('AUTHORS.rst')
history = read('HISTORY.rst').replace('.. :changelog:', '')
licence = read('LICENSE.rst')
readme = read('README.rst')

requirements = read('requirements.txt').splitlines() + [
    'setuptools',
]

test_requirements = read('requirements-dev.txt').splitlines()

setup(
    name='multinosetests',
    version='0.2.1',
    author='Miroslav Shubernetskiy',
    description='Helper utility to run multiple nosetests suites. '
                'Useful for makefile scripts.',
    long_description='\n\n'.join([readme, history, authors, licence]),
    url='http://10.134.8.70/Dealertrack/multinosetests',
    packages=find_packages(exclude=['test', 'test.*']),
    entry_points={
        'console_scripts': [
            'multinosetests = multinosetests:main',
        ]
    },
    install_requires=requirements,
    test_suite='tests',
    tests_require=test_requirements,
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
