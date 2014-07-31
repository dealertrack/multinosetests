from __future__ import unicode_literals, print_function
import sys

from .multinosetests import NosetestsCall, parser, status_print


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
    NosetestsCall.merge_calls(nose_calls, not any_failed)

    sys.exit(0 if not any_failed else 1)
