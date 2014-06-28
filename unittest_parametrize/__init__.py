"""
Let's assume we have a (somewhat trivial, in fact) function that checks
whether the given number is even or not:

>>> def is_even(n):
...     return n % 2 == 0

We could test it just like that:

>>> import unittest
>>> class Test_is_even(unittest.TestCase):
...
...     def test_even(self):
...         for n in [0, 2, -14]:
...             self.assertTrue(is_even(n))
...
...     def test_odd(self):
...         for n in [-1, 17]:
...             self.assertFalse(is_even(n))
...
>>> import sys
>>> def run_tests(test_case_cls):
...     suite = unittest.TestLoader().loadTestsFromTestCase(test_case_cls)
...     unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even ... ok
test_odd ... ok
...
Ran 2 tests...
OK

For such a trivial function it seems to be enough but in the real world
our code units and their tests are more complex, and usually it is a bad
idea to test many cases in one test case method (harder debugging, lack
of test separation...).  Let's parametrize it:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand([0, 2, -14])
...     def test_even(self, n):
...         self.assertTrue(is_even(n))
...
...     @expand([-1, 17])
...     def test_odd(self, n):
...         self.assertFalse(is_even(n))
...
...     def setUp(self):
...         # just to demonstrate that particular tests are really separated
...         sys.stdout.write(' [Note: separate setUp] ')
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even :: -14 ... [Note: separate setUp] ok
test_even :: 0 ... [Note: separate setUp] ok
test_even :: 2 ... [Note: separate setUp] ok
test_odd :: -1 ... [Note: separate setUp] ok
test_odd :: 17 ... [Note: separate setUp] ok
...
Ran 5 tests...
OK

Another approach could be to define one test method with a couple
of arguments:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand([
...         (-14, True),
...         (-1, False),
...         (0, True),
...         (2, True),
...         (17, False),
...     ])
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: -1,False ... ok
test_is_even :: -14,True ... ok
test_is_even :: 0,True ... ok
test_is_even :: 17,False ... ok
test_is_even :: 2,True ... ok
...
Ran 5 tests...
OK

It can also be written in more descriptive way, i.e. using keyword
arguments (especially useful when there are more test method parameters):

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand([
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ])
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: -1,expected=False ... ok
test_is_even :: -14,expected=True ... ok
test_is_even :: 0,expected=True ... ok
test_is_even :: 17,expected=False ... ok
test_is_even :: 2,expected=True ... ok
...
Ran 5 tests...
OK

But what to do, if we need to *label* our parameters explicitly?
We could use a dict:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand({
...         'sys.maxsize': param(sys.maxsize, expected=False),
...         '-sys.maxsize': param(-sys.maxsize, expected=False),
...     })
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: -sys.maxsize ... ok
test_is_even :: sys.maxsize ... ok
...
Ran 2 tests...
OK

...or just the with_label() method of `param` objects:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand([
...         param(1.2345, expected=False).with_label('noninteger'),
...         param('%s', expected=False).with_label('string'),
...     ])
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: noninteger ... ok
test_is_even :: string ... ok
...
Ran 2 tests...
OK

But now, how to unite separately defined param sequences/sets/dicts?
Let's transform them into `paramseq` instances and just *add*:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     basic_params = paramseq([
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ])
...
...     huge_params = paramseq({
...         'sys.maxsize': param(sys.maxsize, expected=False),
...         '-sys.maxsize': param(-sys.maxsize, expected=False),
...     })
...
...     strange_params = paramseq(
...         # using kwargs: the same as passing a dict
...         noninteger=param(1.2345, expected=False),
...         string=param('%s', expected=False),
...     )
...
...     # just add them!
...     all_params = basic_params + huge_params + strange_params
...
...     @expand(all_params)
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: -1,expected=False ... ok
test_is_even :: -14,expected=True ... ok
test_is_even :: -sys.maxsize ... ok
test_is_even :: 0,expected=True ... ok
test_is_even :: 17,expected=False ... ok
test_is_even :: 2,expected=True ... ok
test_is_even :: noninteger ... ok
test_is_even :: string ... ok
test_is_even :: sys.maxsize ... ok
...
Ran 9 tests...
OK

Note that the sets/sequences/dicts/paramseq instances do not need
to be created or bound within the class body -- you could e.g. import
them from a separate module.  Obviously, it makes code reuse and
refactorization easier.

>>> from random import randint

Some testing frameworks provide possibility to combine different
parameter sets to produce cartesian product of their elements...
It's a nice and useful feature -- and we don't want to be inferior!

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     FROM = -(10 ** 6)
...     TO = 10 ** 6
...
...     @paramseq
...     def randomized(cls):
...         yield param(randint(cls.FROM, cls.TO) * 2,
...                     expected=True).with_label('random even')
...         yield param(randint(cls.FROM, cls.TO) * 2 + 1,
...                     expected=False).with_label('random odd')
...
...     input_values_and_results = randomized + [
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ]
...
...     input_types = dict(
...         integer=int,
...         float=float,
...     )
...
...     @expand(input_values_and_results)
...     @expand(input_types)
...     def test_is_even(self, input_type, n, expected):
...         n = input_type(n)
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even :: float, -1,expected=False ... ok
test_is_even :: float, -14,expected=True ... ok
test_is_even :: float, 0,expected=True ... ok
test_is_even :: float, 17,expected=False ... ok
test_is_even :: float, 2,expected=True ... ok
test_is_even :: float, random even ... ok
test_is_even :: float, random odd ... ok
test_is_even :: integer, -1,expected=False ... ok
test_is_even :: integer, -14,expected=True ... ok
test_is_even :: integer, 0,expected=True ... ok
test_is_even :: integer, 17,expected=False ... ok
test_is_even :: integer, 2,expected=True ... ok
test_is_even :: integer, random even ... ok
test_is_even :: integer, random odd ... ok
...
Ran 14 tests...
OK



"""

import unittest
unittest.TextTestRunner

from unittest_parametrize._internal import (
    Context as context,
    Label as label,
    Param as param,
    ParamSeq as paramseq,
    parametrize,
    expand,
)

__all__ = (
    'context',
    'label',
    'param',
    'paramseq',
    'parametrize',
    'expand',
)
