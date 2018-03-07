import testrunner
import pytest
import mock
import os
WRAPPER_FOLDER = 'env'
FILEPATH = os.path.join(WRAPPER_FOLDER, 'a.cpp')
TEST_FOLDER = os.path.join(WRAPPER_FOLDER, 'tests_custom')
TEST_FILES = ['test1', 'test2', 'test10', 'test101', 'test503']


@pytest.fixture()
def setup_files():
    os.mkdir(WRAPPER_FOLDER)
    open(FILEPATH, 'w').close()
    os.mkdir(TEST_FOLDER)
    for filename in TEST_FILES[::-1]:
        open(os.path.join(TEST_FOLDER, filename), 'w').close()


@pytest.mark.usefixtures('fs', 'setup_files')
class TestTestRunner:
    @mock.patch('testrunner.subprocess.call')
    def setup(self, call):
        self.runner = testrunner.TestRunner(FILEPATH, TEST_FOLDER)
        assert(call.call_count == 1)
        act_compile = ' '.join(call.call_args[0][0])
        exp_compile = 'g++ '+FILEPATH+' -o '+testrunner.COMPILE_OUT
        assert(act_compile).startswith(exp_compile)

    @mock.patch('testrunner.subprocess.call')
    def test_constructor_with_no_test_folder(self, call):
        with pytest.raises(ValueError):
            testrunner.TestRunner(FILEPATH, None)

    @mock.patch('testrunner.subprocess.call')
    def test_constructor_with_default_test_folder(self, call):
        exp_folder = os.path.join(WRAPPER_FOLDER,
                                  testrunner.DEFAULT_TESTS_FOLDER)
        os.mkdir(exp_folder)
        runner = testrunner.TestRunner(FILEPATH, None)
        assert(runner.test_folder == exp_folder)

    @mock.patch('testrunner.subprocess.call')
    def test_constructor_invalid_filepath_throws_exception(self, call):
        with pytest.raises(ValueError):
            testrunner.TestRunner('nonexistentfile', TEST_FOLDER)

    @mock.patch.object(testrunner.TestRunner, '_run_test')
    def test_run_tests(self, run_test):
        self.runner.run_tests()
        assert(run_test.call_count == len(TEST_FILES))
        for i in range(len(TEST_FILES)):
            path = os.path.join(TEST_FOLDER, TEST_FILES[i])
            assert(run_test.call_args_list[i][0][0] == (path))
