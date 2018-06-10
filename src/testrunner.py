import filecmp
import re
import subprocess
import logging
import os

logger = logging.getLogger('check')
GCC_FLAGS = ['-D', 'TEST_ENVIRONMENT']
COMPILE_OUT = os.path.join('.', 'run')
DELIM = '======\n'


class TestRunner:
    """Module that runs the tests.

    Attributes:
        test_path (str): path for tests

    Todo:
        * encapsulate test_path, GCC_FLAGS, DELIM into
          a config class/file
    """
    def __init__(self, source_filepath, test_path):
        if not os.path.isfile(source_filepath):
            raise ValueError('Program file %s does not exist' %
                             source_filepath)
        self._compile(source_filepath)
        dirname = os.path.dirname(source_filepath)
        if not os.path.isdir(test_path):
            raise ValueError('Invalid test_path \'%s\'' % test_path)
        self.test_path = test_path

    def _compile(self, source_filepath):
        logger.debug('compiling')
        subprocess.call(['g++', source_filepath, '-o', COMPILE_OUT] +
                        GCC_FLAGS)

    def run_tests(self):
        def first_integer(val):
            re_digit = re.compile(r'(\d+)')
            m = re_digit.search(val)
            if m:
                return int(m.group(1))
        tests = os.listdir(self.test_path)
        tests = list(filter(lambda x: first_integer(x), tests))
        for filename in sorted(tests, key=lambda x: first_integer(x)):
            if '.' in filename:
                continue
            match = self._run_test(os.path.join(self.test_path, filename))
            print('%s: %s' % (filename, 'PASSed' if match else 'FAILed'))

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
        """Separate test file into an input and output file"""
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
