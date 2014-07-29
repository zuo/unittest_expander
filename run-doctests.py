#!/usr/bin/env python

import doctest
import sys

import unittest_expander

if __name__ == '__main__':
    failed, attempted = doctest.testmod(unittest_expander)
    msg = 'Test summary: {1}/{0} passed and {2}/{0} failed.'.format(
            attempted, attempted - failed, failed)
    if failed:
        sys.exit(msg)
    else:
        print(msg)

