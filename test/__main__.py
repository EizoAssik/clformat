#encoding=utf-8
"""
To run tests, run `python -m test`
"""
from . import clformat
from . import utils
from .base import UTestSuite

from sys import modules
from logging import log, DEBUG


def main():
    for name in modules:
        if name.startswith('test.'):
            module = modules[name]
            if 'CASES' in dir(module):
                print('Running test on {}'.format(name))
                suite = UTestSuite(module.CASES)
                suite.run()
                print('Done\n')


if __name__ is '__main__':
    main()