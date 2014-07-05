from setuptools import setup, find_packages

setup(
    name='unittest_expander',
    version='0.1',
    packages = find_packages(),

    author='Jan Kaliszewski',
    author_email='zuo@kaliszewski.net',
    description='Easy and flexible unittest parameterization.',
    long_description=(
        'A library of flexible and easy-to-use tools to parameterize '
        '(multiply by specified params) your unit tests, especially '
        'those using the standard unittest module.'),
    license='MIT',
    keywords='unittest testing parameterization parametrization',
    url='https://github.com/zuo/unittest_expander',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Testing',
    ],
)
