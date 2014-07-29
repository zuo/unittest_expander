Quick Start
===========

*unittest_expander* is a library that provides flexible and
easy-to-use tools to parameterize your unit tests, especially those
based on :class:`unittest.TestCase` from the Python standard library.

:Author: Jan Kaliszewski (zuo)
:License: MIT License
:Homepage: https://github.com/zuo/unittest_expander

Installing
----------

The easiest way to install the library is to execute (possibly in a
`virtualenv`_) the command::

    pip install unittest_expander

.. _virtualenv: https://virtualenv.pypa.io/en/latest/virtualenv.html

(if you do not have the *pip* tool installed -- see:
https://pip.pypa.io/en/latest/installing.html).

Alternatively, you can download the library source tarball, unpack it,
``cd`` to the unpacked directory and execute the following command::

    python setup.py install

(you may need to have administrator privileges, especially if you are
executing it *not* in a *virtualenv*).


Usage example
-------------

Consider the following **ugly** test::

    import unittest

    class Test(unittest.TestCase):
        def test_sum(self):
            for iterable, expected in [
                ([], 0),
                ([0], 0),
                ([3], 3),
                ([1, 3, 1], 5),
                (set([1, 3]), 4),
                ({1:'a', 3:'b'}, 4),
            ]:
                self.assertEqual(sum(iterable), expected)

Is it cool?  **Not at all!**  So let's improve it::

    import unittest
    from unittest_expander import expand, foreach

    @expand
    class Test(unittest.TestCase):
        @foreach([
            ([], 0),
            ([0], 0),
            ([3], 3),
            ([1, 3, 1], 5),
            (set([1, 3]), 4),
            ({1:'a', 3:'b'}, 4),
        ])
        def test_sum(self, iterable, expected):
            self.assertEqual(sum(iterable), expected)

Now you have **7 distinct tests** (properly *isolated* and being
always *reported as separate test cases*) which, however, share the
same test method source.

You may want to do the same in a bit more verbose and descriptive
way::

    import unittest
    from unittest_expander import expand, foreach, param

    @expand
    class Test(unittest.TestCase):

        test_sum_params = [
            param([], expected=0).label('empty gives 0'),
            param([0], expected=0),
            param([3], expected=3),
            param([1, 3, 1], expected=5),
            param(set([1, 3]), expected=4),
            param({1:'a', 3:'b'}, expected=4).label('even dict is ok'),
        ]

        @foreach(test_sum_params)
        def test_sum(self, iterable, expected):
            self.assertEqual(sum(iterable), expected)

This is only a fraction of the possibilities *unittest_expander*
offers to you.

You can **learn more** from the actual documentation of the
*unittest_expander* module.
