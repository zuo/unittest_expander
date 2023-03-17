#!/usr/bin/env python

import doctest
import sys

import unittest_expander


def main():
    failed, attempted = doctest.testmod(unittest_expander)
    msg = 'Test summary: {1}/{0} passed and {2}/{0} failed.'.format(
            attempted, attempted - failed, failed)
    if failed:
        sys.exit(msg)
    else:
        print(msg)


if __name__ == '__main__':
    main()
