#!/usr/bin/env python

import os.path as osp
import re
import sys

import unittest_expander


SETUP_FILENAME = 'setup.cfg'
VERSION_LINE_REGEX = re.compile(br'''
    ^
    version
    \s*
    =
    \s*
    (?P<version_str>
        \S+
    )
    \s*
    $
''', re.VERBOSE)


def get_version_from_setup():
    setup_cfg_path = osp.join(osp.dirname(__file__), SETUP_FILENAME)
    with open(setup_cfg_path, 'rb') as f:
        for line in f:
            match = VERSION_LINE_REGEX.search(line)
            if match:
                return match.group('version_str').decode('utf-8')
    sys.exit('Error: version not found in {!r}.'.format(setup_cfg_path))


def main():
    ver_module = unittest_expander.__version__
    ver_setup = get_version_from_setup()
    if ver_module == ver_setup:
        print('Version number consistency check: OK.')
    else:
        sys.exit(
            'Error: unittest_expander.__version__ ({!r}) differs '
            'from the version number from {} ({!r})'.format(
                ver_module,
                SETUP_FILENAME,
                ver_setup))


if __name__ == '__main__':
    main()
