#!/usr/bin/env python

import doctest

import unittest_expander

if __name__ == '__main__':
    failed, attempted = doctest.testmod(unittest_expander)
    if not failed:
        print('{0} tests passed and {1} failed.'.format(attempted, failed))
