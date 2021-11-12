import re

from setuptools import setup


VERSION_REGEX = re.compile(b'''
    ^
    release
    \s*
    =
    \s*
    ['"]
    (?P<version>
        [^'"]+
    )
    ['"]
    \s*
    $
''', re.VERBOSE)


def get_version():
    with open('docs/conf.py', 'rb') as f:
        for line in f:
            match = VERSION_REGEX.search(line)
            if match:
                return match.group('version').decode('utf-8')
    raise AssertionError('version not specified')


if __name__ == "__main__":
    setup(version=get_version())
