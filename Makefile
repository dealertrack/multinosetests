.PHONY: clean-pyc clean-build clean

NOSE_FLAGS=-sv --rednose
COVER_CONFIG_FLAGS=--with-coverage --cover-package=multinosetests,tests --cover-tests
COVER_REPORT_FLAGS=--cover-html --cover-html-dir=htmlcov
COVER_FLAGS=${COVER_CONFIG_FLAGS} ${COVER_REPORT_FLAGS}

help:

	@echo "install - install all requirements including for testing"
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-coverage - run tests with coverage report"
	@echo "test-all - run tests on every Python version with tox"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "check - run all necessary steps to check validity of project"

install:
	pip install -U -r requirements-dev.txt

clean: clean-build clean-pyc
	@-rm -rf htmlcov/
	@-rm -rf .coverage coverage*

clean-build:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info

clean-pyc:
	-@find . -name '*.pyc' -follow -print0 | xargs -0 rm -f
	-@find . -name '*.pyo' -follow -print0 | xargs -0 rm -f
	-@find . -name '__pycache__' -type d -follow -print0 | xargs -0 rm -rf

lint:
	flake8 multinosetests tests
	importanize --ci

test:
	nosetests ${NOSE_FLAGS} tests/

test-coverage:
	nosetests ${NOSE_FLAGS} ${COVER_FLAGS} tests/

test-all:
	tox

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

check: clean lint test-coverage
