*unittest_expander* is a Python library that provides flexible and
easy-to-use tools to parametrize your unit tests, especially (but
not limited to) those based on *unittest.TestCase*.

The library is compatible with Python 3.11, 3.10, 3.9, 3.8, 3.7, 3.6 and
2.7, and does not depend on any external packages (i.e., uses only the
Python standard library).

:Authors: `Jan Kaliszewski (zuo)`_ and `others...`_
:License: `MIT License`_
:Home Page: https://github.com/zuo/unittest_expander
:Documentation: https://unittest-expander.readthedocs.io/en/stable/

.. _Jan Kaliszewski (zuo): https://github.com/zuo/
.. _others...: https://github.com/zuo/unittest_expander/pulls?q=is%3Apr+is%3Amerged
.. _MIT License: https://github.com/zuo/unittest_expander/blob/main/LICENSE.txt


Installing
----------

The easiest way to install the library is to execute (preferably in a
`virtualenv`_) the command::

    python -m pip install unittest_expander

(note that you need network access to do it this way).  If you do not
have the *pip* tool installed -- see:
https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

Alternatively, you can `download`_ the library source archive, unpack
it, ``cd`` to the unpacked directory and execute (preferably in a
`virtualenv`_) the following command::

    python -m pip install .

Note: you may need to have administrator privileges if you do *not*
operate in a *virtualenv*.

It is also possible to use the library without installing it: as its
code is contained in a single file (``unittest_expander.py``), you can
just copy it into your project.

.. _virtualenv: https://packaging.python.org/tutorials/installing-packages/#creating-and-using-virtual-environments

.. _download: https://pypi.org/project/unittest_expander/#files


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
                (frozenset({1, 3}), 4),
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
            (frozenset({1, 3}), 4),
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
            param(frozenset({1, 3}), expected=4),
            param({1:'a', 3:'b'}, expected=4).label('even dict is ok'),
        ]

        @foreach(test_sum_params)
        def test_sum(self, iterable, expected):
            self.assertEqual(sum(iterable), expected)

This is only a fraction of the possibilities *unittest_expander*
offers to you.

You can **learn more** from the actual `documentation of the module
<https://unittest-expander.readthedocs.io/en/stable/narrative_documentation.html>`_.
