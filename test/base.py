"""
Utils to simplify the code that really handles the trouble.
"""
import unittest
import logging


class UTest(unittest.TestCase):
    def __init__(self, logger_name='CLFormat', method_name=None):
        super().__init__(method_name)
        self.logger_name = logger_name

    def setUp(self):
        self.cases = None
        self.logger = logging.Logger(self.logger_name,
                                     level=logging.DEBUG)
        self.set_cases()
        if self.cases is None:
            self.cases = []

    def set_cases(self):
        pass

    def test_func(self, *args, **kwargs):
        pass

    def log(self, *args):
        self.logger.error(' '.join(args))

    def test_run(self):
        for ctrl, *args, result in self.cases:
            # self.log('CTRL:', ctrl)
            # self.log('ARGS:', str(args))
            # self.log('EXCEPTED RESULT:', result)
            self.assertEqual(self.test_func(ctrl, args), result)
            # self.log('PASS')


class UTestSuite():
    def __init__(self, classes=None):
        self.suite = unittest.TestSuite()
        for cls in classes:
            self.suite.addTest(cls(method_name="test_run"))
        self.runner = unittest.TextTestRunner()

    def run(self):
        self.runner.run(self.suite)