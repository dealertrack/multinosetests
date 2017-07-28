.. :changelog:

History
-------

0.2.2 (2017-07-28)
~~~~~~~~~~~~~~~~~~

* Using wheels for distribution
* Excluding tests from being installed

0.2.1 (2014-08-28)
~~~~~~~~~~~~~~~~~~

* Modified project to use cookiecutter project template

0.2.0 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Added overall test suites test results to print out at the end

0.1.1 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Log output goes to stderr.
  This fixes an issue when ``multinosetests`` is run in CI
  which would result in printing log messages below all test suites.
* Added tests
* Switched to using Python ``setuptools`` entry-points instead of
  binary script

0.1.0 (2014-07-07)
~~~~~~~~~~~~~~~~~~

* Initial release
