from __future__ import unicode_literals, print_function
import mock
import unittest

from multinosetests import NosetestsCall


TESTING_MODULE = 'multinosetests.multinosetests'


class TestNosetestsCall(unittest.TestCase):
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
                         '.coverage.{}'.format(hash(cmd)))

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
                         'nosetests.{}.xml'.format(hash(self.cmd)))

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

    @mock.patch(TESTING_MODULE + '.merge_xunit')
    @mock.patch(TESTING_MODULE + '.call')
    @mock.patch('os.unlink')
    @mock.patch.object(NosetestsCall, 'write_coverage')
    def test_merge_calls(self,
                         mock_write_coverage,
                         mock_unlink,
                         mock_call,
                         mock_merge_xunit):
        cmd = 'nosetests foo --with-xunit --with-coverage --cover-package=bar'
        nose = NosetestsCall(cmd)

        NosetestsCall.merge_calls([nose], True)

        mock_call.assert_any_call('coverage combine', shell=True)
        mock_call.assert_any_call('coverage report --include="bar*"', shell=True)
        mock_write_coverage.assert_called_once_with()
        mock_unlink.assert_called_once_with(nose.xunit_file)
        mock_merge_xunit.assert_called_once_with([nose.xunit_file], 'nosetests.xml')
