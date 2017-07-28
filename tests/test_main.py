from __future__ import print_function, unicode_literals
import unittest

import mock

from multinosetests import main


TESTING_MODULE = 'multinosetests'


def mock_error(string):
    """
    Error function which raises ValueError with given string
    """
    raise ValueError(string)


class TestMultiNoseTests(unittest.TestCase):
    """
    Tests for the main multinosetests function
    which will be triggered when used in shell.
    """

    def setUp(self):
        super(TestMultiNoseTests, self).setUp()
        self.invalid_cmd = 'nosetests foo bar'
        self.valid_cmd = 'nosetests foo bar --with-xunit --with-coverage'

    @mock.patch(TESTING_MODULE + '.parser')
    def test_main_invalid(self, mock_parser):
        mock_parser.parse_args.return_value = mock_parser
        mock_parser.command = [self.invalid_cmd]
        mock_parser.error.side_effect = mock_error

        regex = r'^\n\nErrors found in nosetests commands:.*'
        with self.assertRaisesRegexp(ValueError, regex):
            main()

    @mock.patch(TESTING_MODULE + '.status_print', mock.MagicMock())
    @mock.patch('sys.exit')
    @mock.patch(TESTING_MODULE + '.NosetestsCall')
    @mock.patch(TESTING_MODULE + '.parser')
    def test_main_valid_success(self,
                                mock_parser,
                                mock_nosetests,
                                mock_sys_exit):
        mock_parser.parse_args.return_value = mock_parser
        mock_parser.command = [self.valid_cmd]
        mock_nose = mock.MagicMock()
        mock_nose.return_value = 0
        mock_nosetests.return_value = mock_nose

        main()

        mock_nosetests.merge_calls.assert_called_once_with(
            [mock_nose],
            report_coverage=True
        )
        mock_sys_exit.assert_called_once_with(0)

    @mock.patch(TESTING_MODULE + '.status_print', mock.MagicMock())
    @mock.patch('sys.exit')
    @mock.patch(TESTING_MODULE + '.NosetestsCall')
    @mock.patch(TESTING_MODULE + '.parser')
    def test_main_valid_failure(self,
                                mock_parser,
                                mock_nosetests,
                                mock_sys_exit):
        mock_parser.parse_args.return_value = mock_parser
        mock_parser.command = [self.valid_cmd]
        mock_nose = mock.MagicMock()
        mock_nose.return_value = 5
        mock_nosetests.return_value = mock_nose

        main()

        mock_nosetests.merge_calls.assert_called_once_with(
            [mock_nose],
            report_coverage=False
        )
        mock_sys_exit.assert_called_once_with(1)
