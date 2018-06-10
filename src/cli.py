#!/usr/bin/env python3
import argparse
import logging
from . import testrunner
logging.basicConfig(level=logging.INFO)
DEFAULT_TESTS_FOLDER = 'tests'
DESC = """Compile program and run against tests.

Tests are stored in %s/ folder, with the input and output separated by
the delimeter""" % DEFAULT_TESTS_FOLDER
EP = "EX: %(prog)s a.cpp"


def main():
    parser = argparse.ArgumentParser(description=DESC, epilog=EP)
    parser.add_argument('source_path', type=str,
                        help='source code to compile')
    parser.add_argument('-t', '--test-path', metavar='f', default=DEFAULT_TESTS_FOLDER,
                        help='folder containing tests')
    args = parser.parse_args()
    run(args)


def run(args):
    t = testrunner.TestRunner(args.source_path, args.test_path)
    t.run_tests()
    t.cleanup()


if __name__ == '__main__':
    main()
