from __future__ import print_function, unicode_literals
import argparse
import sys

import six

from .multinosetests import NosetestsCall, status_print


parser = argparse.ArgumentParser(
    description='Run nosetests multiple times and merge their '
                'xml reports using xunitmerge. The advantage '
                'of this plugin is that it guarantees that all '
                'nosetests calls are executed even if any of them '
                'fails. This is especially useful if multiple '
                'nosetests need to be run in Makefile and fail only '
                'after all runs are executed and if any of the '
                'runs failed.'
)

parser.add_argument(
    'command',
    action='store',
    type=six.text_type,
    nargs='+',
    help='Nosetests command string which be executed in shell '
         '(e.g. `nosetests -sv --with-coverage --with-xunit`). '
         'Must contain a flag --with-xunit and can be '
         'provided multiple times.')


def main():
    args = parser.parse_args()

    # initialize all nosetests suites
    nose_calls = [NosetestsCall(command) for command in args.command]

    # if any of the calls have invalid commands
    # print out errors
    if any([not nose.is_valid() for nose in nose_calls]):
        errors = []
        for nose in nose_calls:
            errors.extend(nose.errors)
        errors = map(lambda error: '* ' + error, errors)
        parser.error('\n\nErrors found in nosetests commands:\n{}'
                     ''.format('\n'.join(errors)))

    # execute nosetests suites and check if any failed
    return_calls = [nose() for nose in nose_calls]
    any_failed = any((code != 0 for code in return_calls))

    status_print('Finished running all nosetest suites')

    # merge the test suites and print out the combined
    # coverage report only if none of the test suites failed
    NosetestsCall.merge_calls(
        nose_calls,
        report_coverage=not any_failed
    )

    sys.exit(0 if not any_failed else 1)
