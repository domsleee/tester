import testrunner
import pytest
import mock
import os
WRAPPER_FOLDER = 'env'
FILEPATH = os.path.join(WRAPPER_FOLDER, 'a.cpp')
EXEC = FILEPATH+'_out'
TEST_FOLDER = os.path.join(WRAPPER_FOLDER, 'tests_custom')
TEST_FILES = ['test1', 'test2', 'test10', 'test101', 'test503']

FILE_IN = '''hi there\n'''
FILE_EXP = '''ok\n'''
FILE_TXT = FILE_IN+testrunner.DELIM+FILE_EXP

@pytest.fixture()
def setup_files_cpp():
    os.mkdir(WRAPPER_FOLDER)
    open(FILEPATH, 'w').close()
    open(EXEC, 'w').close()
    os.chmod(EXEC, 755)

    os.mkdir(TEST_FOLDER)
    for filename in TEST_FILES[::-1]:
        open(os.path.join(TEST_FOLDER, filename), 'w').close()

@pytest.mark.usefixtures('fs', 'setup_files_cpp')
class TestTestRunner:
    @mock.patch('testrunner.subprocess.call')
    def setup(self, call):
        self.runner = testrunner.TestRunner(FILEPATH, TEST_FOLDER, False)
        assert(call.call_count == 1)
        act_compile = ' '.join(call.call_args[0][0])
        exp_compile = 'g++ '+FILEPATH+' -o '+EXEC
        assert(act_compile).startswith(exp_compile)

    @mock.patch('testrunner.subprocess.call')
    def test_constructor_with_valid_test_folder(self, call):
        exp_folder = os.path.join(WRAPPER_FOLDER, 'tests')
        os.mkdir(exp_folder)
        runner = testrunner.TestRunner(FILEPATH, exp_folder, False)
        assert(runner.test_path == exp_folder)

    @mock.patch('testrunner.subprocess.call')
    def test_constructor_invalid_sourcefilepath_throws_exception(self, call):
        with pytest.raises(ValueError):
            testrunner.TestRunner('nonexistentfile', TEST_FOLDER, False)

    @mock.patch.object(testrunner.TestRunner, '_run_test')
    def test_run_tests_arguments(self, run_test):
        self.runner.run_tests()
        assert(run_test.call_count == len(TEST_FILES))
        for i in range(len(TEST_FILES)):
            path = os.path.join(TEST_FOLDER, TEST_FILES[i])
            assert(run_test.call_args_list[i][0] == (path+'.in', path+'.exp'))

    @mock.patch.object(testrunner.TestRunner, 'split_file')
    @mock.patch.object(testrunner.TestRunner, '_run_test')
    @mock.patch('testrunner.os.remove')
    def test_split_file_arguments(self, os_remove, run_test, split_file):
        self.runner.run_tests()
        assert(run_test.call_count == len(TEST_FILES))
        for i in range(len(TEST_FILES)):
            path = os.path.join(TEST_FOLDER, TEST_FILES[i])
            assert(split_file.call_args_list[i][0] == (path, path+'.in', path+'.exp', testrunner.DELIM))

    def test_split_file(self):
        test_filename = os.path.join(TEST_FOLDER, 'zzzzzzzz')
        with open(test_filename, 'w') as fout:
            fout.write(FILE_TXT)

        self.runner.split_file(test_filename, test_filename+'.in', test_filename+'.exp', testrunner.DELIM)
        with open(test_filename+'.in', 'r') as fin:
            assert(fin.read() == FILE_IN)
        with open(test_filename+'.exp', 'r') as fin:
            assert(fin.read() == FILE_EXP)

    @mock.patch('testrunner.subprocess.call')
    def test_run_test(self, call):
        test_filename = os.path.join(TEST_FOLDER, 'zzzzzzzz')
        test_filename_in = test_filename + '.in'
        test_filename_exp = test_filename + '.exp'
        test_filename_out = test_filename + '.out'
        subprocess_out = FILE_EXP

        def call_side(*args, **kwargs):
            global subprocess_out
            kwargs.get('stdout').write(subprocess_out)
        call.side_effect = call_side

        def set_in_exp_subprocess(in_txt, exp_txt, subprocess_txt):
            global subprocess_out
            with open(test_filename_in, 'w') as fout:
                fout.write(in_txt)
            with open(test_filename_exp, 'w') as fout:
                fout.write(exp_txt)
            subprocess_out = subprocess_txt

        set_in_exp_subprocess(FILE_IN, FILE_EXP, FILE_EXP)
        assert(self.runner._run_test(test_filename_in, test_filename_exp))
        set_in_exp_subprocess(FILE_IN, FILE_EXP+'\nextra line in expected file, failed', FILE_EXP)
        assert(not self.runner._run_test(test_filename_in, test_filename_exp))
        set_in_exp_subprocess(FILE_IN, FILE_EXP, FILE_EXP+'\nextra line in subprocess file, failed')
        assert(not self.runner._run_test(test_filename_in, test_filename_exp))
