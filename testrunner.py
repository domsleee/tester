import filecmp
import re
from subprocess import call
import subprocess
import logging
import os

logger = logging.getLogger('check')
GCC_FLAGS = ['-D', 'TEST_ENVIRONMENT']
COMPILE_NAME = 'run'
COMPILE_OUT = os.path.join('.', COMPILE_NAME)
DEFAULT_TESTS_FOLDER = 'tests'
DELIM = '======\n'


class TestRunner:
    def __init__(self, source_filepath, arg_test_folder):
        if not os.path.isfile(source_filepath):
            raise ValueError('Program file %s does not exist' %
                             source_filepath)
        self._compile(source_filepath)
        self.test_folder = self._get_test_folder(arg_test_folder)

    def _get_test_folder(self, arg_test_folder):
        test_folder = None
        if arg_test_folder:
            test_folder = arg_test_folder
        else:
            test_folder = os.path.join(os.getcwd(), DEFAULT_TESTS_FOLDER)
        if not os.path.isdir(test_folder):
            raise ValueError('Invalid testing folder provided')
        return test_folder

    def _compile(self, source_filepath):
        logger.debug('compiling')
        call(['g++', source_filepath, '-o', COMPILE_NAME] + GCC_FLAGS)

    def run_tests(self):
        def first_digit(val):
            re_digit = re.compile(r'(\d)+')
            m = re_digit.search(val)
            if m:
                return int(m.group(1))
        tests = os.listdir(self.test_folder)
        tests = list(filter(lambda x: first_digit(x), tests))
        for filename in sorted(tests, key=lambda x: first_digit(x)):
            if '.' in filename:
                continue
            match = self._run_test(os.path.join(self.test_folder, filename))
            print('%s: %s' % (filename, 'Success' if match else 'FAIL'))

    def _run_test(self, test):
        logger.debug('running test %s' % test)
        in_file = test+'.in'
        exp_file = test+'.exp'
        out_file = test+'.out'
        self.split_file(test, in_file, exp_file, DELIM)
        with open(out_file, 'w') as outfile:
            with open(in_file, 'r') as infile:
                subprocess.call(COMPILE_OUT, stdin=infile, stdout=outfile)
        match = filecmp.cmp(exp_file, out_file)
        if match:
            for file in [in_file, exp_file, out_file]:
                os.remove(file)
        return match

    def split_file(self, filepath, in_file, out_file, delim):
        files = [open(in_file, 'w'), open(out_file, 'w')]
        i = 0
        with open(filepath, 'r') as file:
            for line in file:
                if line == delim:
                    i = 1
                else:
                    files[i].write(line)
        for file in files:
            file.close()

    def cleanup(self):
        os.remove(COMPILE_OUT)
