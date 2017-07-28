from __future__ import print_function, unicode_literals
import os
import re
import sys
from subprocess import call

import blessings
import six
import xunitparser
from xunitmerge import merge_xunit


COVERAGE_FILE = '.coverage{}'
NOSETESTS_FILE = 'nosetests{}.xml'
COVER_PACKAGE_RE = re.compile(r'--cover-package=(?P<packages>[a-z0-9_,]+)',
                              re.IGNORECASE)

terminal = blessings.Terminal()


def status_print(status, message=None):
    """
    Helper to print status messages with
    bold formatted status text

    Parameters
    ----------
    status : str
        Status text. Is printed bold.
    message : str, optional
        Optional additional message which will be
        printed next to the status without any formatting.
    """
    message = message or ''
    printout = (
        '\n'
        '---\n'
        '{status}{message}'
        '\n\n'
    )
    printout = printout.format(
        status=terminal.bold_blue(status),
        message=': ' + message if message else '',
    )
    print(printout, file=sys.stderr)


def get_nose_xml_report(path):
    """
    Get the report from the xml nosetests report
    """
    report = xunitparser.parse(open(path))[1]
    errors = len(report.errors)
    failures = len(report.failures)
    return {
        'total': report.testsRun,
        'errors': errors,
        'failures': failures,
        'successful': report.testsRun - errors - failures,
        'is_successful': report.wasSuccessful(),
    }


def status_print_report(name, report, call=None):
    """
    Print out the test suite report
    """
    command = ''
    if call:
        command = call.get_final_command() + '\n'

    _ = lambda x: x  # noqa
    c = getattr(terminal, 'green' if report['is_successful'] else 'red')

    success = 'SUCCESS' if report['is_successful'] else 'FAILURE'

    message = '\n'.join([
        '',
        '{command}',
        c('     result: {success}'),
        _('total tests: {total}'),
        _(' successful: {successful}'),
        _('   failures: {failures}'),
        _('     errors: {errors}'),
    ]).format(command=command, success=success, **report)

    status_print(name, message)


class NosetestsCall(object):
    """
    Interface class for executing a single nosetests command

    Parameters
    ----------
    command : str
        Shell command as string to be executed to run nosetests suite.
        The command must contain ``--with-xunit`` nosetests flag

    Attributes
    ----------
    command : str
        Same as ``command`` parameter
    errors : list
        List of error strings if the input command is not valid
    """

    def __init__(self, command):
        self.command = command
        self.errors = []
        self.return_code = None
        self.coverage_data = None

    def is_valid(self):
        """
        Return boolean if the provided nosetests command is valid

        If any errors are found, they are added
        to the ``errors`` attribute

        The following are the requirements:

        * ``--with-xunit`` must be provided because all nosetests
          xml reports are required to be combined
        * ``--xunit-file`` cannot be provided since multinosetests
          will use a unique filename for the xml report
        """
        self.errors = []

        if '--with-xunit' not in self.command:
            self.errors.append('--with-xunit must be provided in `{}`'
                               ''.format(self.command))

        if '--xunit-file' in self.command:
            self.errors.append('--xunit-file cannot be provided in `{}`'
                               ''.format(self.command))

        return not bool(self.errors)

    def is_covered(self):
        """
        Return boolean if the nosetests command should run with coverage
        """
        return '--with-coverage' in self.command

    @property
    def coverage_file(self):
        """
        Return unique name of the coverage file where the coverage
        data will be stored

        Why a unique filename is required, please refer to ``write_coverage()``
        """
        return COVERAGE_FILE.format('.' + six.text_type(abs(hash(self))))

    def read_coverage(self):
        """
        Read the coverage binary data into memory and
        store it in attribute ``coverage_data``,
        then remove the coverage file

        The reason why above has to happen is primarily to handle
        multiple nosetests suites. Coverage is a clever package
        so if after the first test suite run, the generated
        .coverage file is renamed to something else, on the
        second tests suite run, coverage will notice existing
        coverage file (even if it not called .coverage) and wont
        create a new .coverage file. It will simply append coverage
        data to coverage file from first test suite. As a result,
        when the coverage report will be printed for the second
        test suite, its coverage data will be skewed since it will
        include data from different coverage run. The solution is to
        remove the coverage file between the test suites and once
        all test suites are executed, all coverage data is written
        out to unique files and merged to generate a single complete
        and accurate overall coverage report via
        ``coverage combine`` command.
        """
        with open(COVERAGE_FILE.format(''), 'rb') as fid:
            self.coverage_data = fid.read()
        os.unlink(COVERAGE_FILE.format(''))

    def write_coverage(self):
        """
        Write coverage binary data stored in ``coverage_data``
        attribute back to a unique file

        As described in ``read_coverage()``, coverage files are
        removed in between test suites however after all suites
        are executes, all the coverage data needs to be written
        back to file-system. However if each test suite would
        write back coverage data to ``.coverage`` file, that
        would result in conflicts. Therefore each test suite
        needs to write data back into unique filenames.
        Then all coverage files can be merged into a single
        report via ``coverage combine`` command since it is
        able to find all coverage-like files in a directory.

        There is one catch how unique filenames are generated.
        Instead of generating completely random filenames
        which would clog the directory if for some reason
        coverage files would not be combined, the filenames
        are deterministically generated by using a Python
        string hash of the given nosetests command.
        This way the same nosetests suite will always generate
        the same unique coverage file.
        """
        with open(self.coverage_file, 'wb') as fid:
            fid.write(self.coverage_data)

    @property
    def xunit_file(self):
        """
        Return unique name for nosetests xml xml report
        """
        return NOSETESTS_FILE.format('.{}'.format(abs(hash(self))))

    def get_final_command(self):
        """
        Get the final nosetests command which will be executed

        The given nosetests command in the ``__init__`` is not
        actually executed because some additional flags might
        need to be added. This method adds all necessary flags
        and returns the final command string to be executed.
        """
        return ('{} --xunit-file={}'
                ''.format(self.command,
                          self.xunit_file))

    def __hash__(self):
        """
        Return hash of the given command.
        This hash is used to generate unique files
        related to the nosetests command.

        By hashing a known constant string, its hash result
        is deterministic. Practically this means that if
        multiple nosetests are executed, their unique
        filenames for coverage data and nosetests report
        will always be the same.
        """
        return hash(self.command)

    def __str__(self):
        return str(self.command)

    def __call__(self):
        """
        Execute the nosetests command to run test suite
        and return the return code of the nosetests command

        If the nosetests command includes coverage,
        coverage file is temporarily read into memory
        and is removed from the filesystem.
        Please refer to ``read_coverage()`` for more info.
        """
        command = self.get_final_command()

        status_print('Running', command)
        self.return_code = call(command, shell=True)

        if self.is_covered():
            # coverage report has to be opened and removed
            # because coverage for other suite runs is smart
            # enough to combine the coverage reports
            # on the spot which can cause funny reports
            # for non-first nosetests calls
            self.read_coverage()

        return self.return_code

    @staticmethod
    def merge_calls(nose_calls, report_coverage=True):
        """
        Helper static method to combine all nosetests test suites

        This method primarily combines the nosetests xml reports
        and coverage data if any of the tests had coverage enabled

        Parameters
        ----------
        nose_calls : list
            List of ``NosetestsCall`` class instances to be merged
        report_report_coverage : bool
            Whether to print out the final combined coverage report
        """
        # if any of the test suites had coverage
        # coverage data should be combined
        if any((i.is_covered() for i in nose_calls)):
            [i.write_coverage() for i in nose_calls]
            call('coverage combine', shell=True)

            if report_coverage:
                # find all packages which need to be covered
                # from all nosetests suites and convert to
                # file path patterns compatible with ``--include``
                # coverage flag vs just a list of package names
                # for example package names ``--include=foo,bar``
                # vs filename patterns ``--include=foo*,bar*``
                packages = []
                for nose in nose_calls:
                    find_packages = COVER_PACKAGE_RE.findall(nose.command)
                    if find_packages:
                        packages += find_packages[0].split(',')
                packages = map(lambda j: '{}*'.format(j), list(set(packages)))

                coverage_command = [
                    'coverage',
                    'report',
                    '--include="{}"'.format(','.join(packages)),
                ]
                call(' '.join(coverage_command), shell=True)

        # print out the test report for each test suite
        for suite in nose_calls:
            status_print_report(
                'Test suite report',
                get_nose_xml_report(suite.xunit_file),
                suite,
            )

        # merge all xml reports and remove individual xml reports
        xunit_files = [i.xunit_file for i in nose_calls]
        merge_xunit(xunit_files, NOSETESTS_FILE.format(''))
        list(map(os.unlink, xunit_files))

        # print out the overall tests report
        status_print_report(
            'Overall test suite report',
            get_nose_xml_report(NOSETESTS_FILE.format('')),
        )
