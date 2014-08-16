*unittest_expander* is a Python library that provides flexible and
easy-to-use tools to parameterize your unit tests, especially those
based on *unittest.TestCase*.

The library is compatibile with Python 2.6, 2.7, 3.2, 3.3 and 3.4, and
does not depend on external packages (uses only the Python standard
library).

:Author: Jan Kaliszewski (zuo)
:License: MIT License
:Homepage: https://github.com/zuo/unittest_expander
:Documentation: http://unittest-expander.readthedocs.org/

Installing
----------

The easiest way to install the library is to execute (possibly in a
`virtualenv`_) the command::

    pip install unittest_expander

.. _virtualenv: https://virtualenv.pypa.io/en/latest/virtualenv.html

(note that you need network access to do it this way; if you do not
have the *pip* tool installed -- see:
https://pip.pypa.io/en/latest/installing.html).

Alternatively, you can `download`_ the library source archive, unpack
it, ``cd`` to the unpacked directory and execute the following
command::

    python setup.py install

.. _download: https://pypi.python.org/pypi/unittest_expander#downloads

(you may need to have administrator privileges and/or network access,
especially if you are executing it *not* in a *virtualenv*).

It is also possible to use the library not installing it at all: as
its code is contained in a single file: ``unittest_expander.py``, you
can just copy it into your project.


Usage example
-------------

Consider the following **ugly** test:

.. code:: python

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

Is it cool?  **Not at all!**  So let's improve it:

.. code:: python

    import unittest
    from unittest_expander import expand, foreach

    @expand
    class Test(unittest.TestCase):
        @foreach(
            ([], 0),
            ([0], 0),
            ([3], 3),
            ([1, 3, 1], 5),
            (set([1, 3]), 4),
            ({1:'a', 3:'b'}, 4),
        )
        def test_sum(self, iterable, expected):
            self.assertEqual(sum(iterable), expected)

Now you have **6 distinct tests** (properly *isolated* and being
always *reported as separate tests*), although they share the same
test method source.

You may want to do the same in a bit more verbose and descriptive
way:

.. code:: python

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

You can **learn more** from the actual `documentation of the module
<http://unittest-expander.readthedocs.org/en/latest/narrative_documentation.html>`_.
