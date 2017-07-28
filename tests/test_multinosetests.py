from __future__ import print_function, unicode_literals
import sys
import unittest

import mock

from multinosetests.multinosetests import (
    NosetestsCall,
    get_nose_xml_report,
    status_print,
    status_print_report,
    terminal,
)


TESTING_MODULE = 'multinosetests.multinosetests'


class TestNosetestsCall(unittest.TestCase):
    """
    Tests for NosetestsCall class and its methods
    which implement most of the multinosetests logic
    """

    def setUp(self):
        super(TestNosetestsCall, self).setUp()
        self.cmd = 'nosetests foo bar rainbows'

    def test_init(self):
        """
        Test that __init__ instantiates all necessary attributes
        """
        nose = NosetestsCall('foo')
        self.assertEqual(nose.command, 'foo')
        self.assertListEqual(nose.errors, [])
        self.assertIsNone(nose.return_code)
        self.assertIsNone(nose.coverage_data)

    def test_is_valid(self):
        nose = NosetestsCall('')
        actual = nose.is_valid()
        self.assertFalse(actual)
        self.assertListEqual(
            nose.errors,
            ['--with-xunit must be provided in ``']
        )

        cmd = '--with-xunit --xunit-file'
        nose = NosetestsCall(cmd)
        actual = nose.is_valid()
        self.assertFalse(actual)
        self.assertListEqual(
            nose.errors,
            ['--xunit-file cannot be provided in `{}`'.format(cmd)]
        )

        cmd = '--xunit-file'
        nose = NosetestsCall(cmd)
        actual = nose.is_valid()
        self.assertFalse(actual)
        self.assertListEqual(
            nose.errors,
            [
                '--with-xunit must be provided in `{}`'.format(cmd),
                '--xunit-file cannot be provided in `{}`'.format(cmd)
            ]
        )

        cmd = 'nosetests --with-xunit'
        nose = NosetestsCall(cmd)
        actual = nose.is_valid()
        self.assertTrue(actual)
        self.assertListEqual(nose.errors, [])

    def test_is_covered(self):
        cmd = 'nosetests'
        nose = NosetestsCall(cmd)
        self.assertFalse(nose.is_covered())

        cmd = 'nosetests --with-coverage'
        nose = NosetestsCall(cmd)
        self.assertTrue(nose.is_covered())

    def test_coverage_file(self):
        cmd = 'nosetests foo bar rainbows'
        nose = NosetestsCall(cmd)
        self.assertEqual(nose.coverage_file,
                         '.coverage.{}'.format(abs(hash(cmd))))

    @mock.patch('os.unlink')
    def test_read_coverage(self, mock_unlink):
        mock_open = mock.mock_open(read_data='foo bar')

        nose = NosetestsCall(self.cmd)
        with mock.patch(TESTING_MODULE + '.open', mock_open, create=True):
            nose.read_coverage()

        mock_open.assert_any_call('.coverage', 'rb')
        mock_unlink.assert_called_once_with('.coverage')
        self.assertEqual(nose.coverage_data, 'foo bar')

    def test_write_coverage(self):
        mock_open = mock.mock_open()

        nose = NosetestsCall(self.cmd)
        nose.coverage_data = 'foo bar'
        with mock.patch(TESTING_MODULE + '.open', mock_open, create=True):
            nose.write_coverage()

        mock_open.assert_any_call(nose.coverage_file, 'wb')
        mock_open.return_value.write.assert_called_once_with('foo bar')

    def test_xunit_file(self):
        nose = NosetestsCall(self.cmd)
        self.assertEqual(nose.xunit_file,
                         'nosetests.{}.xml'.format(abs(hash(self.cmd))))

    def test_get_final_command(self):
        nose = NosetestsCall(self.cmd)
        actual = nose.get_final_command()
        self.assertEqual(
            actual,
            self.cmd + ' --xunit-file={}'.format(nose.xunit_file)
        )

    def test_hash(self):
        nose = NosetestsCall(self.cmd)
        self.assertEqual(hash(nose), hash(self.cmd))

    def test_str(self):
        nose = NosetestsCall(self.cmd)
        self.assertEqual(str(nose), str(self.cmd))

    @mock.patch(TESTING_MODULE + '.status_print', mock.MagicMock())
    @mock.patch(TESTING_MODULE + '.call')
    @mock.patch.object(NosetestsCall, 'read_coverage')
    @mock.patch.object(NosetestsCall, 'is_covered')
    def test_call(self,
                  mock_is_covered,
                  mock_read_coverage,
                  mock_call):
        mock_is_covered.return_value = True
        mock_call.return_value = 0

        nose = NosetestsCall(self.cmd)
        actual = nose()

        self.assertEqual(actual, 0)
        mock_call.assert_called_once_with(nose.get_final_command(), shell=True)
        mock_is_covered.assert_called_once_with()
        mock_read_coverage.assert_called_once_with()

    @mock.patch(TESTING_MODULE + '.status_print_report')
    @mock.patch(TESTING_MODULE + '.get_nose_xml_report')
    @mock.patch(TESTING_MODULE + '.merge_xunit')
    @mock.patch(TESTING_MODULE + '.call')
    @mock.patch('os.unlink')
    @mock.patch.object(NosetestsCall, 'write_coverage')
    def test_merge_calls(self,
                         mock_write_coverage,
                         mock_unlink,
                         mock_call,
                         mock_merge_xunit,
                         mock_get_tests_xml_report,
                         mock_status_print_report):
        cmd = 'nosetests foo --with-xunit --with-coverage --cover-package=bar'
        nose = NosetestsCall(cmd)

        NosetestsCall.merge_calls([nose], True)

        mock_call.assert_any_call('coverage combine', shell=True)
        mock_call.assert_any_call('coverage report --include="bar*"',
                                  shell=True)
        mock_write_coverage.assert_called_once_with()
        mock_unlink.assert_called_once_with(nose.xunit_file)
        mock_merge_xunit.assert_called_once_with([nose.xunit_file],
                                                 'nosetests.xml')
        mock_get_tests_xml_report.assert_has_calls([
            mock.call(nose.xunit_file),
            mock.call('nosetests.xml'),
        ])
        mock_status_print_report.assert_has_calls([
            mock.call('Test suite report',
                      mock_get_tests_xml_report.return_value,
                      nose),
            mock.call('Overall test suite report',
                      mock_get_tests_xml_report.return_value,)
        ])


class TestUtils(unittest.TestCase):
    """
    Tests for utility functions used in multinosetests
    """

    @mock.patch(TESTING_MODULE + '.print', create=True)
    @mock.patch(TESTING_MODULE + '.terminal')
    def test_status_print_with_message(self,
                                       mock_terminal,
                                       mock_print):
        mock_terminal.bold_blue.side_effect = lambda x: x

        status_print('foo', 'bar')

        mock_terminal.bold_blue.assert_called_once_with('foo')
        mock_print.assert_called_once_with(
            '\n---\nfoo: bar\n\n',
            file=sys.stderr
        )

    @mock.patch(TESTING_MODULE + '.print', create=True)
    @mock.patch(TESTING_MODULE + '.terminal')
    def test_status_print_without_message(self,
                                          mock_terminal,
                                          mock_print):
        mock_terminal.bold_blue.side_effect = lambda x: x

        status_print('foo')

        mock_terminal.bold_blue.assert_called_once_with('foo')
        mock_print.assert_called_once_with(
            '\n---\nfoo\n\n',
            file=sys.stderr
        )

    @mock.patch(TESTING_MODULE + '.open', create=True)
    @mock.patch('xunitparser.parse')
    def test_get_nose_xml_report(self,
                                 mock_parse,
                                 mock_open):
        report = mock.MagicMock()
        report.errors = [None] * 5
        report.failures = [None] * 7
        report.wasSuccessful.return_value = True
        report.testsRun = 20
        mock_parse.return_value = None, report

        actual = get_nose_xml_report('foo')

        mock_open.assert_called_once_with('foo')
        mock_parse.assert_called_once_with(mock_open.return_value)
        self.assertDictEqual(
            actual,
            {
                'total': 20,
                'errors': 5,
                'failures': 7,
                'successful': 8,
                'is_successful': True,
            }
        )

    @mock.patch(TESTING_MODULE + '.status_print')
    def test_status_print_report_with_call(self, mock_status_print):
        mock_call = mock.MagicMock()
        mock_call.get_final_command.return_value = 'hello'

        report = {
            'total': 20,
            'errors': 5,
            'failures': 7,
            'successful': 8,
            'is_successful': False,
        }

        status_print_report('Foo', report, mock_call)

        mock_status_print.assert_called_once_with(
            'Foo',
            '\n'.join([
                '',
                'hello',
                '',
                terminal.red('     result: FAILURE'),
                'total tests: 20',
                ' successful: 8',
                '   failures: 7',
                '     errors: 5',
            ])
        )

    @mock.patch(TESTING_MODULE + '.status_print')
    def test_status_print_report_without_call(self, mock_status_print):
        report = {
            'total': 20,
            'errors': 5,
            'failures': 7,
            'successful': 8,
            'is_successful': True,
        }

        status_print_report('Foo', report)

        mock_status_print.assert_called_once_with(
            'Foo',
            '\n'.join([
                '',
                '',
                terminal.green('     result: SUCCESS'),
                'total tests: 20',
                ' successful: 8',
                '   failures: 7',
                '     errors: 5',
            ])
        )
