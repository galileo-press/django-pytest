
from django.test.simple import DjangoTestSuiteRunner
from pkg_resources import load_entry_point
import sys

class TestRunner (DjangoTestSuiteRunner):

    def run_tests(self, test_labels, extra_tests=None):
        # Remove stop word (--) from argument list again. This separates Django
        # command options from py.test ones.
        try:
            cut = sys.argv.index('--')
            args = sys.argv[:cut]
            options = sys.argv[cut+1:]
        except ValueError:
            args = sys.argv[1:]
            options = []

        # Filter out any option that was not meant for py.test (like "-v2").
        # TODO deal with options that take arguments (so far not used)
        args = filter(lambda x: x in ('-s', '-x', '-k', '--pdb'), args)

        try:
            entry_point = load_entry_point('py>=1.0.0', 'console_scripts', 'py.test')
        except ImportError:
            entry_point = load_entry_point('pytest>=2.0', 'console_scripts', 'py.test')

        self.setup_test_environment()
        old_config = self.setup_databases()
        result = entry_point(args + options)
        self.teardown_databases(old_config)
        self.teardown_test_environment()

        # TODO return number of failures and errors
        return result