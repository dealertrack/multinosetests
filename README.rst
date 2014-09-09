==============
MultiNoseTests
==============

.. image:: https://badge.fury.io/py/multinosetests.png
    :target: http://badge.fury.io/py/multinosetests

.. image:: https://travis-ci.org/dealertrack/multinosetests.png?branch=master
    :target: https://travis-ci.org/dealertrack/multinosetests

.. image:: https://coveralls.io/repos/dealertrack/multinosetests/badge.png?branch=master
    :target: https://coveralls.io/r/dealertrack/multinosetests?branch=master

Helper utility to run multiple nosetests suites.
Mostly used for making makefile scripts.

This utility runs multiple nosetest suites and merges their
xml reports using xunitmerge. The advantage of this utility
is that it guarantees that all nosetests suites are executed
even if any of them fails (exit status ``>0``). This is especially
useful if multiple nosetests need to be run in Makefile script
because normally, if any of them will fail, the rest of the
script wont get executed which will skew the nosetests xml
report as well as coverage data which are especially useful
for CI systems such as Jenkins.

Installing
----------

You can install ``multinosetests`` using pip::

    $ pip install multinosetests

Using
-----

You can use the utility via an executable ``multinosetests``::

    $ multinosetests --help
    $ multinosetests "nosetests tests/foo -sv --with-xunit --with-coverage" \
                     "nosetests tests/bar -sv --with-xunit --with-coverage"

Testing
-------

To run the tests you need to install testing requirements first::

    $ pip install -r requirements-dev.txt

Then to run tests, you can use ``nosetests``::

    $ nosetests -sv
