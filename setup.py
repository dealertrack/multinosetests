from __future__ import print_function, unicode_literals
import os

from setuptools import find_packages, setup


def read(fname):
    with open(os.path.abspath(os.path.join(__file__, os.pardir, fname)), 'rb') as fid:
        return fid.read().decode('utf-8')


authors = read('AUTHORS.rst')
history = read('HISTORY.rst').replace('.. :changelog:', '')
licence = read('LICENSE.rst')
readme = read('README.rst')

requirements = read('requirements.txt').splitlines() + [
    'setuptools',
]

test_requirements = (
    read('requirements.txt').splitlines() +
    read('requirements-dev.txt').splitlines()[1:]
)

setup(
    name='multinosetests',
    version='0.2.2',
    author='Miroslav Shubernetskiy',
    description='Helper utility to run multiple nosetests suites. '
                'Useful for makefile scripts.',
    long_description='\n\n'.join([readme, history, authors, licence]),
    url='https://github.com/Dealertrack/multinosetests',
    packages=find_packages(exclude=['tests', 'tests.*']),
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
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
)
