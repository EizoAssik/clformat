#encoding=utf-8
"""
Test cases for the clformat.clformat
"""

from .base import UTest, UTestSuite
from clformat import clformat


class UTCLFormat(UTest):
    def test_func(self, *args, **kwargs):
        return clformat(None, *args)

    def test_run(self):
        for *args, result in self.cases:
            self.assertEqual(self.test_func(*args), result)


class UTestCharFn(UTCLFormat):
    def set_cases(self):
        self.cases = [
            ('~C', 'A', 'A'),
            ('~C', ' ', ' '),
            ('~:C', 'A', 'A'),
            ('~:C', ' ', 'Space'),
            ('~:@C', '^ ', 'Control-Space'),
        ]


class UTestFreshLine(UTCLFormat):
    def set_cases(self):
        self.cases = [
            ('~&', ''),
            ('~42&', '\n' * 41),
            ('~%~2&', '\n\n\n'),
            ('~%->~0&<-', '\n-><-'),
            ('~C~&', '\n', '\n\n'),
        ]


class UTestEscape(UTCLFormat):
    def set_cases(self):
        self.cases = [
            ('~~~%~|', '~\n\f'),
            ('~2~~3%~4|', '~~\n\n\n\f\f\f\f'),
        ]


class UTestRadix(UTCLFormat):
    def set_cases(self):
        self.cases = [
            ("~,,' ,4:B", 13, "1101"),
            ("~,,' ,4:B", 17, "1 0001"),
            ("~19,0,' ,4:B", 3333, "0000 1101 0000 0101"),
            ("~3,,,' ,2:R", 17, "1 22"),
            ("~,,'|,2:D", 65535, "6|55|35")
        ]


CASES = [UTestCharFn, UTestFreshLine, UTestEscape, UTestRadix]
