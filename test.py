#encoding=utf-8
import unittest
import logging

from fn import clformat


class UTest(unittest.TestCase):
    def setUp(self):
        self.clformat_to_str = lambda c, a: clformat(None, c, *a)
        self.cases = None
        self.logger = logging.Logger('CLFormat', level=logging.DEBUG)
        self.set_cases()
        if self.cases is None:
            self.cases = []

    def set_cases(self):
        pass

    def log(self, *args):
        self.logger.error(' '.join(args))

    # @unittest.skip('')
    def test_run(self):
        for ctrl, *args, result in self.cases:
            # self.log('CTRL:', ctrl)
            # self.log('ARGS:', str(args))
            # self.log('EXCEPTED RESULT:', result)
            self.assertEqual(self.clformat_to_str(ctrl, args), result)
            # self.log('PASS')


class UTestCharFn(UTest):
    def set_cases(self):
        self.cases = [
            ('~C', 'A', 'A'),
            ('~C', ' ', ' '),
            ('~:C', 'A', 'A'),
            ('~:C', ' ', 'Space'),
            ('~:@C', '^ ', 'Control-Space'),
        ]


class UTestCLFormat(UTest):
    def _set_cases(self):
        self.cases = [
            ('~{~:A、~%~{~A~A~T~{~W,~}~}~%~}',
             (['一', [1, 2, ['a', 'b']], '二', [1, 2, ['a', 'b']]]), None),
            ('~C <> ~:C <> ~@C <> ~@:C', ('\t', '\t', '\t', 'A'), None)
        ]


def main():
    classes = [UTestCharFn]
    suite = unittest.TestSuite()
    for cls in classes:
        suite.addTest(cls("test_run"))
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
