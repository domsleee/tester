import filecmp
import re
import subprocess
import logging
import os

logger = logging.getLogger('check')
GCC_FLAGS = ['-D', 'TEST_ENVIRONMENT']
DELIM = '======\n'


class TestRunner:
    """Module that runs the tests.

    Attributes:
        test_path (str): path for tests.
        executable (bool): if `source_filepath` is the executable,
                           otherwise it will attempt to compile

    Todo:
        * encapsulate test_path, GCC_FLAGS, DELIM into
          a config class/file.
    """
    def __init__(self, source_filepath, test_path, executable):
        if not os.path.isfile(source_filepath):
            raise ValueError('Program file \'%s\' does not exist' %
                             source_filepath)
        if not os.path.isdir(test_path):
            raise ValueError('Invalid test_path \'%s\'' % test_path)

        self.compile_out = False
        self.test_path = test_path
        ext = os.path.splitext(source_filepath)[1] # file extension

        if executable or ext == '' or re.match(r'py|sh', ext):
            self.executable = os.path.join('.', source_filepath)
        else:
            self.compile_out = source_filepath+'_out'
            self._compile(source_filepath)
            self.executable = os.path.join('.', self.compile_out)

        if not os.access(self.executable, os.X_OK):
            raise ValueError('Executable \'%s\' does not have execute permission' %
                             self.executable)

    def _compile(self, source_filepath):
        logger.debug('compiling')
        try:
            subprocess.call(['g++', source_filepath, '-o', self.compile_out]+
                            GCC_FLAGS)
        except Exception:
            print('Could not compile \'%s\'' % source_filepath)
            raise

    def run_tests(self):
        """Run tests in `self.test_path`.

        Todo:
            * use glob for `tests` for files with numbers, allowing
              a simpler `first_integer`.
        """
        def first_integer(val):
            m = re.search(r'(\d+)', val)
            if m: return int(m.group(1))

        tests = os.listdir(self.test_path)
        tests = list(filter(lambda x: first_integer(x), tests))
        for filename in sorted(tests, key=lambda x: first_integer(x)):
            if '.' in filename:
                continue
            test = os.path.join(self.test_path, filename)
            in_file, exp_file = test+'.in', test+'.exp'
            self.split_file(test, in_file, exp_file, DELIM)
            res = 'PASSed' if self._run_test(in_file, exp_file) else 'FAILed'
            for file in [in_file, exp_file]: os.remove(file)
            print('%s: %s' % (filename, res))

    def _run_test(self, in_file, exp_file):
        logger.debug('running test (%s,%s)' % (in_file, exp_file))
        out_file = in_file.replace('.in', '.out')
        with open(out_file, 'w') as outfile:
            with open(in_file, 'r') as infile:
                try:
                    subprocess.call(self.executable, stdin=infile, stdout=outfile)
                except Exception:
                    print('I have no idea why it would fail here')
                    raise
        match = filecmp.cmp(exp_file, out_file)
        if match:
            for file in [out_file]: os.remove(file)
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
        if self.compile_out:
            os.remove(self.compile_out)
