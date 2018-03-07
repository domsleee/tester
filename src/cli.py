#!/usr/bin/env python3
import argparse
import logging
import testrunner
logging.basicConfig(level=logging.INFO)


DESC = """Compile program and run against tests.

Tests are stored in tests/ folder, with the input and output separated by
the delimeter"""
EP = "%(prog) a.cpp"


def main():
    parser = argparse.ArgumentParser(description=DESC, epilog=EP)
    parser.add_argument('source_path', type=str,
                        help='source code to compile')
    parser.add_argument('--test-folder', '-t',
                        help='specify a different testing folder')
    args = parser.parse_args()
    run(args)


def run(args):
    t = testrunner.TestRunner(args.source_path, args.test_folder)
    t.run_tests()
    t.cleanup()


if __name__ == '__main__':
    main()