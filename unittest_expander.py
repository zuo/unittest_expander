# Copyright (c) 2014-2023 Jan Kaliszewski (zuo) & others. All rights reserved.
#
# Licensed under the MIT License:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
*unittest_expander* is a Python library that provides flexible and
easy-to-use tools to parametrize your unit tests, especially those
based on :class:`unittest.TestCase` from the Python standard library.

The :mod:`unittest_expander` module provides the following tools:

* a test class decorator: :func:`expand`,
* a test method decorator: :func:`foreach`,
* two helper classes: :class:`param` and :class:`paramseq`.

Let's see how to use them...


.. _expand-and-foreach-basics:

Basic use of :func:`expand` and :func:`foreach`
===============================================

Assume we have a function that checks whether the given number is even
or not:

>>> def is_even(n):
...     return n % 2 == 0

Of course, in the real world the code we write is usually more
interesting...  Anyway, most often we want to test how it works for
different parameters.  At the same time, it is not the best idea to
test many cases in a loop within one test method -- because of lack
of test isolation (tests depend on other ones -- they may inherit some
state which can affect their results), less information on failures (a
test failure prevents subsequent tests from being run), less clear
result messages (you don't see at first glance which case is the
actual culprit), etc.

So let's write our tests in a smarter way:

>>> import unittest
>>> from unittest_expander import expand, foreach
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(0, 2, -14)        # call variant #1: parameter collection
...     def test_even(self, n):    # specified using multiple arguments
...         self.assertTrue(is_even(n))
...
...     @foreach([-1, 17])         # call variant #2: parameter collection as
...     def test_odd(self, n):     # one argument being a container (e.g. list)
...         self.assertFalse(is_even(n))
...
...     # just to demonstrate that test cases are really isolated
...     def setUp(self):
...         sys.stdout.write(' [DEBUG: separate test setUp] ')
...         sys.stdout.flush()

As you see, it's fairly simple: you bind parameter collections to your
test methods with the :func:`foreach` decorator and decorate the whole
test class with the :func:`expand` decorator.  The latter does the
actual job, i.e., generates (and adds to the test class) parametrized
versions of the test methods.

Let's run this stuff...

>>> # a helper function that will run tests in our examples --
>>> # NORMALLY YOU DON'T NEED IT, of course!
>>> import sys
>>> def run_tests(*test_case_classes):
...     suite = unittest.TestSuite(
...         unittest.TestLoader().loadTestsFromTestCase(cls)
...         for cls in test_case_classes)
...     unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even__<-14> ... [DEBUG: separate test setUp] ok
test_even__<0> ... [DEBUG: separate test setUp] ok
test_even__<2> ... [DEBUG: separate test setUp] ok
test_odd__<-1> ... [DEBUG: separate test setUp] ok
test_odd__<17> ... [DEBUG: separate test setUp] ok
...Ran 5 tests...
OK

To test our *is_even()* function we created two test methods -- each
accepting one parameter value.

Another approach could be to define a method that accepts a couple of
arguments:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         (-14, True),
...         (-1, False),
...         (0, True),
...         (2, True),
...         (17, False),
...     )
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-1,False> ... ok
test_is_even__<-14,True> ... ok
test_is_even__<0,True> ... ok
test_is_even__<17,False> ... ok
test_is_even__<2,True> ... ok
...Ran 5 tests...
OK

As you see, you can use a tuple to specify several parameter values for
a test call.


.. _param-basics:

More flexibility: :class:`param`
================================

Parameters can be specified in a more descriptive way -- in particular,
using also keyword arguments.  It is possible when you use :class:`param`
objects instead of tuples:

>>> from unittest_expander import param
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     )
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-1,expected=False> ... ok
test_is_even__<-14,expected=True> ... ok
test_is_even__<0,expected=True> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<2,expected=True> ... ok
...Ran 5 tests...
OK

Generated *labels* of our tests (attached to the names of the generated
test methods) became less cryptic.  But what to do if we need to label
our parameters explicitly?

We can use the :meth:`~param.label` method of :class:`param` objects:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         param(sys.maxsize, expected=False).label('sys.maxsize'),
...         param(-sys.maxsize, expected=False).label('-sys.maxsize'),
...     )
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-sys.maxsize> ... ok
test_is_even__<sys.maxsize> ... ok
...Ran 2 tests...
OK

If a test method accepts the `label` keyword argument, the appropriate
label (either auto-generated from parameter values or explicitly
specified with :meth:`param.label`) will be passed in as that
argument:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         param(sys.maxsize, expected=False).label('sys.maxsize'),
...         param(-sys.maxsize, expected=False).label('-sys.maxsize'),
...     )
...     def test_is_even(self, n, expected, label):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...         assert label in ('sys.maxsize', '-sys.maxsize')
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-sys.maxsize> ... ok
test_is_even__<sys.maxsize> ... ok
...Ran 2 tests...
OK


.. _other-ways-to-label:

Other ways to explicitly label your tests
=========================================

You can also label particular tests by passing a dictionary directly
into :func:`foreach`:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach({
...         'noninteger': (1.2345, False),
...         'horribleabuse': ('%s', False),
...     })
...     def test_is_even(self, n, expected, label):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...         assert label in ('noninteger', 'horribleabuse')
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<horribleabuse> ... ok
test_is_even__<noninteger> ... ok
...Ran 2 tests...
OK

...or just using keyword arguments:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         noninteger=(1.2345, False),
...         horribleabuse=('%s', False),
...     )
...     def test_is_even(self, n, expected, label):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...         assert label in ('noninteger', 'horribleabuse')
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<horribleabuse> ... ok
test_is_even__<noninteger> ... ok
...Ran 2 tests...
OK


.. _paramseq-basics:

Smart parameter collection: :class:`paramseq`
=============================================

How to concatenate some separately created parameter collections?

Just transform them (or at least the first of them) into
:class:`paramseq` instances -- and then add one to another
(with the ``+`` operator):

>>> from unittest_expander import paramseq
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     basic_params1 = paramseq(   # init variant #1: several parameters
...         param(-14, expected=True),
...         param(-1, expected=False),
...     )
...     basic_params2 = paramseq([  # init variant #2: one parameter collection
...         param(0, expected=True).label('just zero, because why not?'),
...         param(2, expected=True),
...         param(17, expected=False),
...     ])
...     basic = basic_params1 + basic_params2
...
...     huge = paramseq({  # explicit labelling by passing a dict
...         'sys.maxsize': param(sys.maxsize, expected=False),
...         '-sys.maxsize': param(-sys.maxsize, expected=False),
...     })
...
...     other = paramseq(
...         (-15, False),
...         param(15, expected=False),
...         # explicit labelling with keyword arguments:
...         noninteger=param(1.2345, expected=False),
...         horribleabuse=param('%s', expected=False),
...     )
...
...     just_dict = {
...         '18->True': (18, True),
...     }
...
...     just_list = [
...         param(12399999999999999, False),
...         param(n=12399999999999998, expected=True),
...     ]
...
...     # just add them one to another (producing a new paramseq)
...     all_params = basic + huge + other + just_dict + just_list
...
...     @foreach(all_params)
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-1,expected=False> ... ok
test_is_even__<-14,expected=True> ... ok
test_is_even__<-15,False> ... ok
test_is_even__<-sys.maxsize> ... ok
test_is_even__<15,expected=False> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<18->True> ... ok
test_is_even__<2,expected=True> ... ok
test_is_even__<<12399999999...>,False> ... ok
test_is_even__<expected=True,n=<12399999999...>> ... ok
test_is_even__<horribleabuse> ... ok
test_is_even__<just zero, because why not?> ... ok
test_is_even__<noninteger> ... ok
test_is_even__<sys.maxsize> ... ok
...Ran 14 tests...
OK

.. note::

   Parameter collections -- being *sequences* (e.g., :class:`list`
   instances), or *mappings* (e.g., :class:`dict` instances), or *sets*
   (e.g., :class:`set` or :class:`frozenset` instances), or callable
   objects (see below...), or just ready :class:`paramseq` instances --
   do not need to be created or bound within the test class body; you
   could, for example, import them from a separate module. Obviously,
   that makes data/code reuse and refactorization easier.

   Also, note that the call signatures of :func:`foreach` and the
   :class:`paramseq` constructor are identical: you pass in either
   exactly one positional argument which is a parameter collection, or
   several (more than one) positional and/or keyword arguments being
   :class:`param` instances or tuples of parameter values, or singular
   parameter values.

.. note::

   We said that a parameter collection can be a *sequence* (among
   others; see the note above).  To be more precise: it can be a
   *sequence*, except that it *cannot be*: a :class:`tuple`, a *text
   string* (:class:`str` in Python 3, :class:`str` or :class:`unicode`
   in Python 2) or a Python 3 *binary string-like sequence*
   (:class:`bytes` or :class:`bytearray`).

A :class:`paramseq` instance can also be created from a callable object
(e.g., a function) that returns a *sequence* or another *iterable*
object (e.g., a :term:`generator iterator`):

>>> from random import randint
>>> 
>>> @paramseq   # <- yes, used as a decorator
... def randomized(test_case_cls):
...     LO, HI = test_case_cls.LO, test_case_cls.HI
...     print('DEBUG: LO = {}; HI = {}'.format(LO, HI))
...     print('----')
...     yield param(randint(LO, HI) * 2,
...                 expected=True).label('random even')
...     yield param(randint(LO, HI) * 2 + 1,
...                 expected=False).label('random odd')
...
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     LO = -100
...     HI = 100
...
...     @foreach(randomized)
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
...     # reusing the same instance of paramseq to show that the underlying
...     # callable is called separately for each use of @foreach:
...     @foreach(randomized)
...     def test_is_even_negated_when_incremented(self, n, expected):
...         actual = (not is_even(n + 1))
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
DEBUG: LO = -100; HI = 100
----
DEBUG: LO = -100; HI = 100
----
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<random even> ... ok
test_is_even__<random odd> ... ok
test_is_even_negated_when_incremented__<random even> ... ok
test_is_even_negated_when_incremented__<random odd> ... ok
...Ran 4 tests...
OK

A callable object (such as the :term:`generator` function in the example
above) which is passed to the :class:`paramseq`'s constructor (or
directly to :func:`foreach`) should accept either no arguments or one
positional argument -- in the latter case the *test class* will be
passed in.

.. note::

   The callable object will be called -- and its *iterable* result will
   be iterated over (consumed) -- *when* the :func:`expand` decorator
   is being executed, *directly before* generating parametrized test
   methods.

   What should also be emphasized is that those operations (the
   aforementioned call and iterating over its result) will be
   performed *separately* for each use of :func:`foreach` with our
   :class:`paramseq` instance as its argument (or with another
   :class:`paramseq` instance that includes our instance; see the
   following code snippet in which the ``input_values_and_results``
   instance includes the previously created ``randomized`` instance).

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     LO = -999999
...     HI = 999999
...
...     # reusing the same, previously created, instance of paramseq
...     # (`randomized`) to show that the underlying callable will
...     # still be called separately for each use of @foreach...
...     input_values_and_results = randomized + [
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ]
...
...     @foreach(input_values_and_results)
...     def test_is_even(self, n, expected):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
...     @foreach(input_values_and_results)
...     def test_is_even_negated_when_incremented(self, n, expected):
...         actual = (not is_even(n + 1))
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
DEBUG: LO = -999999; HI = 999999
----
DEBUG: LO = -999999; HI = 999999
----
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-1,expected=False> ... ok
test_is_even__<-14,expected=True> ... ok
test_is_even__<0,expected=True> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<2,expected=True> ... ok
test_is_even__<random even> ... ok
test_is_even__<random odd> ... ok
test_is_even_negated_when_incremented__<-1,expected=False> ... ok
test_is_even_negated_when_incremented__<-14,expected=True> ... ok
test_is_even_negated_when_incremented__<0,expected=True> ... ok
test_is_even_negated_when_incremented__<17,expected=False> ... ok
test_is_even_negated_when_incremented__<2,expected=True> ... ok
test_is_even_negated_when_incremented__<random even> ... ok
test_is_even_negated_when_incremented__<random odd> ... ok
...Ran 14 tests...
OK


.. _foreach-cartesian:

Combining several :func:`foreach` to get Cartesian product
==========================================================

You can apply two or more :func:`foreach` decorators to the same test
method -- to combine several parameter collections, obtaining the
Cartesian product of them:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     # one param collection (7 items)
...     @paramseq
...     def randomized():
...         yield param(randint(-(10 ** 6), 10 ** 6) * 2,
...                     expected=True).label('random even')
...         yield param(randint(-(10 ** 6), 10 ** 6) * 2 + 1,
...                     expected=False).label('random odd')
...     input_values_and_results = randomized + [  # (<- note the use of +)
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ]
...
...     # another param collection (2 items)
...     input_types = dict(
...         integer=int,
...         floating=float,
...     )
...
...     # let's combine them (7 * 2 -> 14 parametrized tests)
...     @foreach(input_values_and_results)
...     @foreach(input_types)
...     def test_is_even(self, input_type, n, expected):
...         n = input_type(n)
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<floating, -1,expected=False> ... ok
test_is_even__<floating, -14,expected=True> ... ok
test_is_even__<floating, 0,expected=True> ... ok
test_is_even__<floating, 17,expected=False> ... ok
test_is_even__<floating, 2,expected=True> ... ok
test_is_even__<floating, random even> ... ok
test_is_even__<floating, random odd> ... ok
test_is_even__<integer, -1,expected=False> ... ok
test_is_even__<integer, -14,expected=True> ... ok
test_is_even__<integer, 0,expected=True> ... ok
test_is_even__<integer, 17,expected=False> ... ok
test_is_even__<integer, 2,expected=True> ... ok
test_is_even__<integer, random even> ... ok
test_is_even__<integer, random odd> ... ok
...Ran 14 tests...
OK

If parameters combined this way specify some conflicting keyword
arguments, they are detected and an error is reported:

>>> params1 = [param(a=1, b=2, c=3)]
>>> params2 = [param(b=4, c=3, d=2)]
>>> 
>>> @expand   # doctest: +ELLIPSIS
... class TestSomething(unittest.TestCase):
...
...     @foreach(params2)
...     @foreach(params1)
...     def test(self, **kw):
...         "something"
...
Traceback (most recent call last):
  ...
ValueError: conflicting keyword arguments: 'b', 'c'


.. _context-basics:

Context-manager-based fixtures: :meth:`param.context`
=====================================================

When dealing with resources managed with `context managers`_, you can
specify a *context manager factory* and its arguments using the
:meth:`~param.context` method of a :class:`param` object -- then each
call of the resultant parametrized test will be enclosed in a dedicated
*context manager* instance (created by calling the *context manager
factory* with the given arguments).

.. _context managers: https://docs.python.org/reference/
   datamodel.html#with-statement-context-managers

>>> from tempfile import NamedTemporaryFile
>>> 
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = [
...         param(save='', load='').context(NamedTemporaryFile, 'w+t'),
...         param(save='abc', load='abc').context(NamedTemporaryFile, 'w+t'),
...     ]
...
...     @foreach(params_with_contexts)
...     def test_save_load(self, save, load, context_targets):
...         file = context_targets[0]
...         file.write(save)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...
...     # reusing the same params to show that a *new* context manager
...     # instance is created for each test call:
...     @foreach(params_with_contexts)
...     def test_save_load_with_spaces(self, save, load, context_targets):
...         file = context_targets[0]
...         file.write(' ' + save + ' ')
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, ' ' + load + ' ')
...
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<load='',save=''> ... ok
test_save_load__<load='abc',save='abc'> ... ok
test_save_load_with_spaces__<load='',save=''> ... ok
test_save_load_with_spaces__<load='abc',save='abc'> ... ok
...Ran 4 tests...
OK
>>> 
>>> # repeating the tests to show that, really, a *new* context manager
... # instance is created for *each* test call:
... run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<load='',save=''> ... ok
test_save_load__<load='abc',save='abc'> ... ok
test_save_load_with_spaces__<load='',save=''> ... ok
test_save_load_with_spaces__<load='abc',save='abc'> ... ok
...Ran 4 tests...
OK

As you can see in the above example, if a test method accepts the
`context_targets` keyword argument then a list of context manager
*as-targets* (i.e., objects returned by context managers'
:meth:`__enter__`) will be passed in as that argument.

It is a list because there can be more than one *context* per parameter
collection's item, e.g.:

>>> import contextlib
>>> @contextlib.contextmanager
... def debug_cm(tag=None):
...     debug.append('enter' + (':{}'.format(tag) if tag else ''))
...     yield tag
...     debug.append('exit' + (':{}'.format(tag) if tag else ''))
...
>>> debug = []
>>> 
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = [
...         (
...             param(save='', load='', expected_tag='FOO')
...               .context(NamedTemporaryFile, 'w+t')  # (outer one)
...               .context(debug_cm, tag='FOO')        # (inner one)
...         ),
...         (
...             param(save='abc', load='abc', expected_tag='BAR')
...               .context(NamedTemporaryFile, 'w+t')
...               .context(debug_cm, tag='BAR')
...         ),
...     ]
...
...     @foreach(params_with_contexts)
...     def test_save_load(self, save, load, expected_tag, context_targets):
...         file, tag = context_targets
...         assert tag == expected_tag
...         file.write(save)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...         debug.append('test')
...
>>> debug == []
True
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<expected_tag='BAR',load='abc',save='abc'> ... ok
test_save_load__<expected_tag='FOO',load='',save=''> ... ok
...Ran 2 tests...
OK
>>> debug == [
...     'enter:BAR', 'test', 'exit:BAR',
...     'enter:FOO', 'test', 'exit:FOO',
... ]
True

Contexts are properly handled (context managers' :meth:`__enter__` and
:meth:`__exit__` are properly called...) also when errors occur (with
some legitimate subtle reservations -- see:
:ref:`contexts-cannot-suppress-exceptions`):

>>> class ErrDebugCM(object):
...
...     def __init__(self, tag):
...         debug.append('init:' + tag)
...         self._tag = tag
...
...     def __enter__(self):
...         if self._tag.endswith('context-enter-error'):
...             debug.append('ERR-enter:' + self._tag)
...             raise RuntimeError('error in __enter__')
...         debug.append('enter:' + self._tag)
...         return self._tag
...
...     def __exit__(self, exc_type, exc_val, exc_tb):
...         if exc_type is None:
...             if self._tag.endswith('context-exit-error'):
...                 debug.append('ERR-exit:' + self._tag)
...                 raise RuntimeError('error in __exit__')
...             debug.append('exit:' + self._tag)
...         else:
...             debug.append('ERR-exit:' + self._tag)
...
>>> debug = []
>>> err_params = [
...     (
...         param().label('no_error')
...                .context(ErrDebugCM, tag='outer')
...                .context(ErrDebugCM, tag='inner')
...     ),
...     (
...         param().label('test_fail')
...                .context(ErrDebugCM, tag='outer')
...                .context(ErrDebugCM, tag='inner')
...     ),
...     (
...         param().label('test_error')
...                .context(ErrDebugCM, tag='outer')
...                .context(ErrDebugCM, tag='inner')
...     ),
...     (
...         param().label('inner_context_enter_error')
...                .context(ErrDebugCM, tag='outer')
...                .context(ErrDebugCM, tag='inner-context-enter-error')
...     ),
...     (
...         param().label('inner_context_exit_error')
...                .context(ErrDebugCM, tag='outer')
...                .context(ErrDebugCM, tag='inner-context-exit-error')
...     ),
...     (
...         param().label('outer_context_enter_error')
...                .context(ErrDebugCM, tag='outer-context-enter-error')
...                .context(ErrDebugCM, tag='inner')
...     ),
...     (
...         param().label('outer_context_exit_error')
...                .context(ErrDebugCM, tag='outer-context-exit-error')
...                .context(ErrDebugCM, tag='inner')
...     ),
... ]
>>> 
>>> @expand
... class SillyTest(unittest.TestCase):
...
...     def setUp(self):
...         debug.append('setUp')
...
...     def tearDown(self):
...         debug.append('tearDown')
...
...     @foreach(err_params)
...     def test(self, label):
...         if label == 'test_fail':
...             debug.append('FAIL-test')
...             self.fail()
...         elif label == 'test_error':
...             debug.append('ERROR-test')
...             raise RuntimeError
...         else:
...             debug.append('test')
...
>>> run_tests(SillyTest)  # doctest: +ELLIPSIS
test__<inner_context_enter_error> ... ERROR
test__<inner_context_exit_error> ... ERROR
test__<no_error> ... ok
test__<outer_context_enter_error> ... ERROR
test__<outer_context_exit_error> ... ERROR
test__<test_error> ... ERROR
test__<test_fail> ... FAIL
...Ran 7 tests...
FAILED (failures=1, errors=5)
>>> debug == [
...     # inner_context_enter_error
...     'setUp',
...     'init:outer',
...     'enter:outer',
...     'init:inner-context-enter-error',
...     'ERR-enter:inner-context-enter-error',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # inner_context_exit_error
...     'setUp',
...     'init:outer',
...     'enter:outer',
...     'init:inner-context-exit-error',
...     'enter:inner-context-exit-error',
...     'test',
...     'ERR-exit:inner-context-exit-error',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # no_error
...     'setUp',
...     'init:outer',
...     'enter:outer',
...     'init:inner',
...     'enter:inner',
...     'test',
...     'exit:inner',
...     'exit:outer',
...     'tearDown',
...
...     # outer_context_enter_error
...     'setUp',
...     'init:outer-context-enter-error',
...     'ERR-enter:outer-context-enter-error',
...     'tearDown',
...
...     # outer_context_exit_error
...     'setUp',
...     'init:outer-context-exit-error',
...     'enter:outer-context-exit-error',
...     'init:inner',
...     'enter:inner',
...     'test',
...     'exit:inner',
...     'ERR-exit:outer-context-exit-error',
...     'tearDown',
...
...     # test_error
...     'setUp',
...     'init:outer',
...     'enter:outer',
...     'init:inner',
...     'enter:inner',
...     'ERROR-test',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # test_fail
...     'setUp',
...     'init:outer',
...     'enter:outer',
...     'init:inner',
...     'enter:inner',
...     'FAIL-test',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...     'tearDown',
... ]
True

Note that contexts are handled *directly* before (by running
:meth:`__enter__`) and after (by running :meth:`__exit__`) each relevant
test method call, that is, *after* the :meth:`setUp` and *before*
:meth:`tearDown` calls (if those :class:`unittest.TestCase`-specific
methods are engaged) -- so :meth:`setUp` and :meth:`tearDown` are
not affected by any errors related to those contexts.

Obviously, if an error in :meth:`setUp` occurs then the test method is
not called at all. Therefore, then, relevant context managers are not
even created:

>>> def setUp(self):
...     debug.append('setUp')
...     raise ValueError
...
>>> SillyTest.setUp = setUp
>>> debug = []
>>> run_tests(SillyTest)  # doctest: +ELLIPSIS
test__<inner_context_enter_error> ... ERROR
test__<inner_context_exit_error> ... ERROR
test__<no_error> ... ERROR
test__<outer_context_enter_error> ... ERROR
test__<outer_context_exit_error> ... ERROR
test__<test_error> ... ERROR
test__<test_fail> ... ERROR
...Ran 7 tests...
FAILED (errors=7)
>>> debug == ['setUp', 'setUp', 'setUp', 'setUp', 'setUp', 'setUp', 'setUp']
True


.. _paramseq-context:

Convenience shortcut: :meth:`paramseq.context`
==============================================

You can use the method :meth:`paramseq.context` to apply the given
context properties to *all* parameter items the :class:`paramseq`
instance aggregates:

>>> @contextlib.contextmanager
... def silly_cm():
...     yield 42
...
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = paramseq(
...         param(save='', load=''),
...         param(save='abc', load='abc'),
...     ).context(NamedTemporaryFile, 'w+t').context(silly_cm)
...
...     @foreach(params_with_contexts)
...     def test_save_load(self, save, load, context_targets):
...         file, silly_cm_target = context_targets
...         assert silly_cm_target == 42
...         file.write(save)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<load='',save=''> ... ok
test_save_load__<load='abc',save='abc'> ... ok
...Ran 2 tests...
OK

It should be noted that :meth:`paramseq.context` as well as
:meth:`param.context` and :meth:`param.label` methods create new objects
(respectively :class:`paramseq` or :class:`param` instances), *without*
modifying the existing ones.

>>> pseq1 = paramseq(1, 2, 3)
>>> pseq2 = pseq1.context(open, '/etc/hostname', 'rb')
>>> isinstance(pseq1, paramseq) and isinstance(pseq2, paramseq)
True
>>> pseq1 is not pseq2
True

>>> p1 = param(1, 2, c=3)
>>> p2 = p1.context(open, '/etc/hostname', 'rb')
>>> p3 = p2.label('one with label')
>>> isinstance(p1, param) and isinstance(p2, param) and isinstance(p3, param)
True
>>> p1 is not p2
True
>>> p2 is not p3
True
>>> p3 is not p1
True

Generally, instances of these types (:class:`param` and :class:`paramseq`)
should be considered immutable.


.. _contexts-cannot-suppress-exceptions:

Contexts cannot suppress exceptions unless you enable that explicitly
=====================================================================

The Python *context manager* protocol provides a way to suppress an
exception occuring in the code enclosed by a context: the exception is
*suppresed* (*not* propagated) if the context manager's
:meth:`__exit__` method returns a *true* value (such as :obj:`True`).

It does **not** apply to context managers declared with
:meth:`param.context` or :meth:`paramseq.context`: if :meth:`__exit__`
of such a context manager returns a *true* value, it is ignored and
the exception (if any) is propagated anyway.  The rationale of this
behavior is that silencing exceptions is generally not a good idea
when dealing with testing (it could easily make your tests leaky and
useless).

However, if you **really** need to allow your context manager to
suppress exceptions, pass the keyword argument ``_enable_exc_suppress_=True``
(note the single underscores at the beginning and the end of its name)
to the :meth:`param.context` or :meth:`paramseq.context` method (and,
of course, make the :meth:`__exit__` context manager's method return a
*true* value).

Here we pass ``_enable_exc_suppress_=True`` to :meth:`param.context`:

>>> class SillySuppressingCM(object):
...     def __enter__(self): return self
...     def __exit__(self, exc_type, exc_val, exc_tb):
...         if exc_type is not None:
...             debug.append('suppressing {}'.format(exc_type.__name__))
...         return True  # suppress any exception
...
>>> @expand
... class SillyExcTest(unittest.TestCase):
...
...     @foreach(
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...     )
...     def test_it(self, test_error):
...         debug.append('raising {}'.format(test_error.__name__))
...         raise test_error('ha!')
...
>>> debug = []
>>> run_tests(SillyExcTest)  # doctest: +ELLIPSIS
test_it__... ok
test_it__... ok
...Ran 2 tests...
OK
>>> debug == [
...     'raising AssertionError',
...     'suppressing AssertionError',
...     'raising KeyError',
...     'suppressing KeyError',
... ]
True

Here we pass ``_enable_exc_suppress_=True`` to :meth:`paramseq.context`:

>>> my_params = paramseq(
...     AssertionError,
...     KeyError,
... ).context(SillySuppressingCM, _enable_exc_suppress_=True)
>>> @expand
... class SecondSillyExcTest(unittest.TestCase):
...
...     @foreach(my_params)
...     def test_it(self, test_error):
...         debug.append('raising {}'.format(test_error.__name__))
...         raise test_error('ha!')
...
>>> debug = []
>>> run_tests(SecondSillyExcTest)  # doctest: +ELLIPSIS
test_it__... ok
test_it__... ok
...Ran 2 tests...
OK
>>> debug == [
...     'raising AssertionError',
...     'suppressing AssertionError',
...     'raising KeyError',
...     'suppressing KeyError',
... ]
True

Yet another example:

>>> class ErrorCM:
...     def __init__(self, error): self.error = error
...     def __enter__(self): return self
...     def __exit__(self, exc_type, exc_val, exc_tb):
...         if exc_type is not None:
...             debug.append('replacing {} with {}'.format(
...                 exc_type.__name__, self.error.__name__))
...         else:
...             debug.append('raising {}'.format(self.error.__name__))
...         raise self.error('argh!')
...
>>> @expand
... class AnotherSillyExcTest(unittest.TestCase):
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=RuntimeError),
...         param(test_error=None)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...         param(test_error=None)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=IndexError, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=TypeError, _enable_exc_suppress_=True),
...         param(test_error=OSError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ValueError)
...             .context(ErrorCM, error=ZeroDivisionError),
...         param(test_error=UnboundLocalError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ValueError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ZeroDivisionError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...     ])
...     def test_it(self, test_error):
...         if test_error is None:
...             debug.append('no error')
...         else:
...             debug.append('raising {}'.format(test_error.__name__))
...             raise test_error('ha!')
...
>>> debug = []
>>> run_tests(AnotherSillyExcTest)  # doctest: +ELLIPSIS
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
...Ran 6 tests...
OK
>>> debug == [
...     'raising AssertionError',
...     'suppressing AssertionError',
...
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...     'suppressing RuntimeError',
...
...     'raising OSError',
...     'replacing OSError with ZeroDivisionError',
...     'replacing ZeroDivisionError with ValueError',
...     'suppressing ValueError',
...
...     'raising UnboundLocalError',
...     'suppressing UnboundLocalError',
...     'raising ZeroDivisionError',
...     'suppressing ZeroDivisionError',
...     'raising ValueError',
...     'suppressing ValueError',
...
...     'no error',
...
...     'no error',
...     'raising TypeError',
...     'replacing TypeError with IndexError',
...     'suppressing IndexError',
... ]
True

Normally -- without ``_enable_exc_suppress_=True`` -- exceptions
*are* propagated even when :meth:`__exit__` returns a *true* value:

>>> @expand
... class AnotherSillyExcTest2(unittest.TestCase):
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=RuntimeError),
...         param(test_error=None)
...             .context(SillySuppressingCM),
...         param(test_error=None)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=IndexError)
...             .context(ErrorCM, error=TypeError),
...         param(test_error=OSError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=ValueError)
...             .context(ErrorCM, error=ZeroDivisionError),
...         param(test_error=UnboundLocalError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=ValueError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=ZeroDivisionError)
...             .context(SillySuppressingCM),
...     ])
...     def test_it(self, test_error):
...         if test_error is None:
...             debug.append('no error')
...         else:
...             debug.append('raising {}'.format(test_error.__name__))
...             raise test_error('ha!')
...
>>> debug = []
>>> run_tests(AnotherSillyExcTest2)  # doctest: +ELLIPSIS
test_it__... FAIL
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... ok
test_it__... ERROR
...Ran 6 tests...
FAILED (failures=1, errors=4)
>>> debug == [
...     # Note that the following 'suppressing ...' messages are lies
...     # because no errors are effectively suppressed here.
...
...     'raising AssertionError',
...     'suppressing AssertionError',
...
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...     'suppressing RuntimeError',
...
...     'raising OSError',
...     'replacing OSError with ZeroDivisionError',
...     'replacing ZeroDivisionError with ValueError',
...     'suppressing ValueError',
...
...     'raising UnboundLocalError',
...     'suppressing UnboundLocalError',
...     'replacing UnboundLocalError with ZeroDivisionError',
...     'suppressing ZeroDivisionError',
...     'replacing ZeroDivisionError with ValueError',
...     'suppressing ValueError',
...
...     'no error',
...
...     'no error',
...     'raising TypeError',
...     'replacing TypeError with IndexError',
...     'suppressing IndexError',
... ]
True

Note that ``_enable_exc_suppress_=True`` changes nothing when context
manager's :meth:`__exit__` returns a *false* value:

>>> @expand
... class AnotherSillyExcTest3(unittest.TestCase):
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True),
...         param(test_error=KeyError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True)
...             .context(ErrorCM, error=RuntimeError),
...         param(test_error=None)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True),
...         param(test_error=None)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True)
...             .context(ErrorCM, error=IndexError, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=TypeError, _enable_exc_suppress_=True),
...         param(test_error=OSError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ValueError)
...             .context(ErrorCM, error=ZeroDivisionError),
...         param(test_error=UnboundLocalError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ValueError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True)
...             .context(ErrorCM, error=ZeroDivisionError)
...             .context(NamedTemporaryFile, 'w+t', _enable_exc_suppress_=True),
...     ])
...     def test_it(self, test_error):
...         if test_error is None:
...             debug.append('no error')
...         else:
...             debug.append('raising {}'.format(test_error.__name__))
...             raise test_error('ha!')
...
>>> debug = []
>>> run_tests(AnotherSillyExcTest3)  # doctest: +ELLIPSIS
test_it__... FAIL
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... ok
test_it__... ERROR
...Ran 6 tests...
FAILED (failures=1, errors=4)
>>> debug == [
...     'raising AssertionError',
...
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...
...     'raising OSError',
...     'replacing OSError with ZeroDivisionError',
...     'replacing ZeroDivisionError with ValueError',
...
...     'raising UnboundLocalError',
...     'replacing UnboundLocalError with ZeroDivisionError',
...     'replacing ZeroDivisionError with ValueError',
...
...     'no error',
...
...     'no error',
...     'raising TypeError',
...     'replacing TypeError with IndexError',
... ]
True


.. _about-substitute:

:class:`Substitute` objects
===========================

One could ask: "What does the :func:`expand` decorator do with the
original methods decorated with :func:`foreach`?"

>>> @expand
... class DummyTest(unittest.TestCase):
...
...     @foreach(1, 2)
...     def test_it(self, x):
...         pass
...
...     attr = [42]
...     test_it.attr = [43, 44]

They cannot be left where they are because, without parametrization,
they are not valid tests (but rather kind of test templates).  For this
reason, they are always replaced (by the :func:`expand`'s machinery)
with :class:`Substitute` instances:

>>> test_it = DummyTest.test_it
>>> test_it                           # doctest: +ELLIPSIS
<...Substitute object at 0x...>
>>> test_it.actual_object             # doctest: +ELLIPSIS
<...test_it...>
>>> test_it.attr
[43, 44]
>>> test_it.attr is test_it.actual_object.attr
True
>>> (set(dir(test_it.actual_object)) - {'__call__'}
...  ).issubset(dir(test_it))
True

As you see, such a :class:`Substitute` instance is kind of a
non-callable proxy to the original method (preventing it from being
included by test loaders, but still keeping it available for
introspection, etc.).


.. _custom-name-formatting:

Custom method name formatting
=============================

If you don't like how parametrized test method names are generated --
you can customize that globally by:

* setting :attr:`expand.global_name_pattern` to a :meth:`~str.format`-able
  pattern, making use of zero or more of the following replacement fields:

  * ``{base_name}`` -- the name of the original test method,
  * ``{base_obj}`` -- the original test method (technically: function)
    object,
  * ``{label}`` -- the test label (automatically generated or
    explicitly specified with :meth:`param.label`),
  * ``{count}`` -- the consecutive number (within a single application
    of :func:`@expand`) of the generated parametrized test method;

  (in future versions of *unittest_expander* more replacement fields may
  be made available)

and/or

* setting :attr:`expand.global_name_formatter` to an instance of a
  custom subclass of the :class:`string.Formatter` class from the
  Python standard library (or to any object whose :meth:`format`
  method acts similarily to :meth:`string.Formatter.format`).

.. doctest::
    :hide:

    >>> expand.global_name_pattern is None
    True
    >>> expand.global_name_formatter is None
    True

For example:

>>> expand.global_name_pattern = '{base_name}__parametrized_{count:04}'
>>>
>>> params_with_contexts = paramseq(
...     param(save='', load=''),
...     param(save='abc', load='abc'),
... ).context(NamedTemporaryFile, 'w+t')
>>>
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...     @foreach(params_with_contexts)
...     @foreach(param(suffix=' '), param(suffix='XX'))
...     def test_save_load(self, context_targets, save, load, suffix):
...         file = context_targets[0]
...         file.write(save + suffix)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load + suffix)
...
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__parametrized_0001 ... ok
test_save_load__parametrized_0002 ... ok
test_save_load__parametrized_0003 ... ok
test_save_load__parametrized_0004 ... ok
...Ran 4 tests...
OK

...or, let's say:

>>> import string
>>> class ExtremelySillyFormatter(string.Formatter):
...     def format(self, format_string, *args, **kwargs):
...         count = kwargs['count']
...         label = kwargs['label']
...         if 'abc' in label:
...             result = 'test__{}__"!!! {} !!!"'.format(count, label)
...         else:
...             result = super(ExtremelySillyFormatter,
...                            self).format(format_string, *args, **kwargs)
...         if count % 3 == 1:
...             result = result.replace('_', '-')
...         return result
...
>>> expand.global_name_formatter = ExtremelySillyFormatter()
>>>
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...     @foreach(params_with_contexts)
...     @foreach(param(suffix=' '), param(suffix='XX'))
...     def test_save_load(self, context_targets, save, load, suffix):
...         file = context_targets[0]
...         file.write(save + suffix)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load + suffix)
...
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test--4--"!!! suffix='XX', load='abc',save='abc' !!!" ... ok
test-save-load--parametrized-0001 ... ok
test__2__"!!! suffix=' ', load='abc',save='abc' !!!" ... ok
test_save_load__parametrized_0003 ... ok
...Ran 4 tests...
OK

Set those attributes to :obj:`None` to restore the default behavior:

>>> expand.global_name_pattern = None
>>> expand.global_name_formatter = None


.. _avoiding-name-clashes:

Name clashes avoided automatically
==================================

:func:`expand` does its best to avoid name conflicts: when it detects
that a newly generated name could clash with an existing one (whether
the latter was generated recently -- as an effect of the ongoing
application of :func:`expand` -- or might have already existed), it
adds a suffix to the newly generated name to avoid the clash.  E.g.:

>>> def setting_attrs(attr_dict):
...     def deco(cls):
...         for k, v in attr_dict.items():
...             setattr(cls, k, v)
...         return cls
...     return deco
...
>>> @expand
... @setting_attrs({
...     'test_even__<4>': 'something',
...     'test_even__<4>__2': None,
... })
... class Test_is_even(unittest.TestCase):
...
...     @foreach(
...         0,
...         4,
...         0,   # <- repeated parameter value
...         0,   # <- repeated parameter value
...         -16,
...         0,   # <- repeated parameter value
...     )
...     def test_even(self, n):
...         self.assertTrue(is_even(n))
...
>>> Function = type(lambda: None)
>>> {name: type(obj)
...  for name, obj in vars(Test_is_even).items()
...  if not name.startswith('_')
... } == {
...     'test_even': Substitute,
...     'test_even__<-16>': Function,
...     'test_even__<0>': Function,
...     'test_even__<0>__2': Function,
...     'test_even__<0>__3': Function,
...     'test_even__<0>__4': Function,
...     'test_even__<4>': str,
...     'test_even__<4>__2': type(None),
...     'test_even__<4>__3': Function,
... }
True
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even__<-16> ... ok
test_even__<0> ... ok
test_even__<0>__2 ... ok
test_even__<0>__3 ... ok
test_even__<0>__4 ... ok
test_even__<4>__3 ... ok
...Ran 6 tests...
OK
>>> @expand
... @setting_attrs({
...     'test_even__<0>__6': False,
...     'test_even__<0>__7': object(),
... })
... class Test_is_even_2(Test_is_even):
...
...     @foreach(
...         0,
...         4,
...         0,   # <- repeated parameter value
...         0,   # <- repeated parameter value
...         -16,
...         0,   # <- repeated parameter value
...     )
...     def test_even(self, n):
...         self.assertTrue(is_even(n))
...
>>> {name: type(obj)
...  for name, obj in vars(Test_is_even_2).items()
...  if not name.startswith('_')
... } == {
...     'test_even': Substitute,
...     'test_even__<-16>__2': Function,
...     'test_even__<0>__10': Function,
...     'test_even__<0>__5': Function,
...     'test_even__<0>__6': bool,
...     'test_even__<0>__7': object,
...     'test_even__<0>__8': Function,
...     'test_even__<0>__9': Function,
...     'test_even__<4>__4': Function,
... }
True
>>> run_tests(Test_is_even_2)  # doctest: +ELLIPSIS
test_even__<-16> ... ok
test_even__<-16>__2 ... ok
test_even__<0> ... ok
test_even__<0>__10 ... ok
test_even__<0>__2 ... ok
test_even__<0>__3 ... ok
test_even__<0>__4 ... ok
test_even__<0>__5 ... ok
test_even__<0>__8 ... ok
test_even__<0>__9 ... ok
test_even__<4>__3 ... ok
test_even__<4>__4 ... ok
...Ran 12 tests...
OK


Questions and answers about various details...
==============================================

"Can I omit :func:`expand` and then apply it to subclasses?"
------------------------------------------------------------

Yes, you can.  Please consider the following example:

>>> debug = []
>>> parameters = paramseq(
...     7, 8, 9,
... ).context(debug_cm, tag='M')  # see earlier definition of debug_cm()...
>>>
>>> class MyTestMixIn(object):
...
...     @foreach(parameters)
...     def test(self, x):
...         debug.append((x, self.n))
...
>>> @expand
... class TestActual(MyTestMixIn, unittest.TestCase):
...     n = 42
...
>>> @expand
... class TestYetAnother(MyTestMixIn, unittest.TestCase):
...     n = 12345
...
>>> run_tests(TestActual, TestYetAnother)  # doctest: +ELLIPSIS
test__<7> (...TestActual...) ... ok
test__<8> (...TestActual...) ... ok
test__<9> (...TestActual...) ... ok
test__<7> (...TestYetAnother...) ... ok
test__<8> (...TestYetAnother...) ... ok
test__<9> (...TestYetAnother...) ... ok
...Ran 6 tests...
OK
>>> inspect.isfunction(vars(MyTestMixIn)['test'])      # (not touched by @expand)
True
>>> type(vars(TestActual)['test']) is Substitute       # (replaced by @expand)
True
>>> type(vars(TestYetAnother)['test']) is Substitute   # (replaced by @expand)
True
>>> debug == [
...     'enter:M', (7, 42), 'exit:M',
...     'enter:M', (8, 42), 'exit:M',
...     'enter:M', (9, 42), 'exit:M',
...     'enter:M', (7, 12345), 'exit:M',
...     'enter:M', (8, 12345), 'exit:M',
...     'enter:M', (9, 12345), 'exit:M',
... ]
True

Note that, most probably, you should name such mix-in or "test template"
base classes in a way that will prevent the test loader you use from
including them; for the same reason, typically, it is better to avoid
making them subclasses of :class:`unittest.TestCase`.


"Can I :func:`expand` a subclass of an already :func:`expand`-ed class?"
------------------------------------------------------------------------

Yes, you can (in some past versions of *unittest_expander* it was
broken, but now it works perfectly):

>>> debug = []
>>> parameters = paramseq(
...     1, 2, 3,
... ).context(debug_cm)  # see earlier definition of debug_cm()...
>>> 
>>> @expand
... class Test(unittest.TestCase):
...
...     @foreach(parameters)
...     def test(self, n):
...         debug.append(n)
...
>>> @expand
... class TestSubclass(Test):
...
...     @foreach(parameters)
...     def test_another(self, n):
...         debug.append(n)
...
>>> run_tests(TestSubclass)  # doctest: +ELLIPSIS
test__<1> (...TestSubclass...) ... ok
test__<2> (...TestSubclass...) ... ok
test__<3> (...TestSubclass...) ... ok
test_another__<1> (...TestSubclass...) ... ok
test_another__<2> (...TestSubclass...) ... ok
test_another__<3> (...TestSubclass...) ... ok
...Ran 6 tests...
OK
>>> type(TestSubclass.test) is type(Test.test) is Substitute
True
>>> type(TestSubclass.test_another) is Substitute
True


"Do my test classes need to inherit from :class:`unittest.TestCase`?"
---------------------------------------------------------------------

No, it doesn't matter from the point of view of the
*unittest_expander* machinery.

>>> debug = []
>>> parameters = paramseq(
...     1, 2, 3,
... ).context(debug_cm)  # see earlier definition of debug_cm()...
>>> 
>>> @expand
... class Test(object):  # not a unittest.TestCase subclass
...
...     @foreach(parameters)
...     def test(self, n):
...         debug.append(n)
...
>>> # confirming that unittest_expander machinery acted properly:
>>> instance = Test()
>>> type(instance.test) is Substitute
True
>>> t1 = getattr(instance, 'test__<1>')
>>> t2 = getattr(instance, 'test__<2>')
>>> t3 = getattr(instance, 'test__<3>')
>>> t1()
>>> t2()
>>> t3()
>>> debug == [
...     'enter', 1, 'exit',
...     'enter', 2, 'exit',
...     'enter', 3, 'exit',
... ]
True


"What happens if I apply :func:`expand` when there's no :func:`foreach`?"
-------------------------------------------------------------------------

Just nothing -- the test works as if :func:`expand` was not applied at
all:

>>> @expand
... class TestIt(unittest.TestCase):
...
...     def test(self):
...         sys.stdout.write(' [DEBUG: OK] ')
...         sys.stdout.flush()
...
>>> run_tests(TestIt)  # doctest: +ELLIPSIS
test ... [DEBUG: OK] ok
...Ran 1 test...
OK


"To what objects can :func:`foreach` be applied?"
-------------------------------------------------

The :func:`foreach` decorator is designed to be applied *only* to
regular test methods (i.e., instance methods, *not* static or class
methods) -- that is, technicaly, to *functions* being attributes of
test (or test mix-in) classes.

You should *not* apply :func:`foreach` to anything else or a
:exc:`TypeError` will be raised:

>>> @foreach(1, 2, 3)
... class What:
...     '''I am not a function'''                   # doctest: +ELLIPSIS
...
Traceback (most recent call last):
  ...
TypeError: ...is not a...

>>> @expand
... class ErroneousTest(unittest.TestCase):
...     @foreach(parameters)
...     @classmethod
...     def test_erroneous(cls, n):
...         '''I am not a function'''               # doctest: +ELLIPSIS
...
Traceback (most recent call last):
  ...
TypeError: ...is not a...


.. doctest::
    :hide:

    Other checks
    ============

    For completeness, let's widen the suite of covered usage cases and
    error conditions...

    >>> isinstance(paramseq(), paramseq)
    True
    >>> isinstance(paramseq(1, 2), paramseq)
    True
    >>> isinstance(paramseq(1, two=2), paramseq)
    True
    >>> isinstance(paramseq(one=1, two=2), paramseq)
    True
    >>> isinstance(paramseq([1, 2]), paramseq)
    True
    >>> isinstance(paramseq({1, 2}), paramseq)
    True
    >>> isinstance(paramseq({'one': 1, 'two': 2}), paramseq)
    True
    >>> isinstance(paramseq(paramseq([1, 2])), paramseq)
    True

    >>> isinstance(paramseq([1, 2]) + {3, 4} + [5, 6], paramseq)
    True
    >>> isinstance({3, 4} + paramseq([1, 2]) + [5, 6], paramseq)
    True

    >>> paramseq([1, 2]) + 123       # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> 123 + paramseq([1, 2])       # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq([1, 2]) + '123'     # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> '123' + paramseq([1, 2])     # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq([1, 2]) + u'123'    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> u'123' + paramseq([1, 2])    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq([1, 2]) + b'123'    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> b'123' + paramseq([1, 2])       # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq([1, 2]) + bytearray(b'123')    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> bytearray(b'123') + paramseq([1, 2])    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq([1, 2]) + (3, 4, 5)    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> (3, 4, 5) + paramseq([1, 2])    # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq(123)                # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> paramseq('123')              # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> paramseq(u'123')             # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> paramseq(b'123')             # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> paramseq(bytearray(b'123'))  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> paramseq((3, 4, 5))          # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach(123)   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach('123')   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach(u'123')   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach(b'123')   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach(bytearray(b'123'))   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach((3, 4, 5))   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand()  # <- effectively, same as `@expand` without `()`
    ... class Test_is_even(unittest.TestCase):
    ...
    ...     params1a = paramseq() + [
    ...         (-14, True),
    ...     ]
    ...     params1b = [
    ...         (-1, False),
    ...     ]
    ...     params1ab = params1a + params1b
    ...
    ...     params1c = [
    ...         (-8, True),
    ...     ]
    ...     params1d = paramseq([
    ...         (-7, False),
    ...     ])
    ...     params1cd = params1c + params1d
    ...
    ...     params1 = params1ab + params1cd
    ...
    ...     params2 = [
    ...         (),
    ...         param(),
    ...         param(0, expected=True),
    ...         (2, True),
    ...         param(17, expected=False),
    ...     ]
    ...
    ...     params3 = paramseq({
    ...         'sys.maxsize': (sys.maxsize, False),
    ...         '-sys.maxsize': (-sys.maxsize, False),
    ...     })
    ...
    ...     params4 = paramseq(
    ...         (-15, False),
    ...         param(15, expected=False),
    ...         noninteger=(1.2345, False),
    ...         horribleabuse=param('%s', expected=False),
    ...     )
    ...
    ...     params5 = {
    ...         '18 -> True': (18, True),
    ...     }
    ...
    ...     params6 = [
    ...         (12399999999999999, False),
    ...         param(n=12399999999999998, expected=True),
    ...     ]
    ...
    ...     @foreach(params1 + params2 + params3 + params4 + params5 + params6)
    ...     @foreach(['Foo'])
    ...     def test_is_even(self, foo, n=0, expected=True):
    ...         self.assertTrue(foo, 'Foo')
    ...         actual = is_even(n)
    ...         self.assertTrue(isinstance(actual, bool))
    ...         self.assertEqual(actual, expected)
    ...
    >>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
    test_is_even__<'Foo', -1,False> ... ok
    test_is_even__<'Foo', -14,True> ... ok
    test_is_even__<'Foo', -15,False> ... ok
    test_is_even__<'Foo', -7,False> ... ok
    test_is_even__<'Foo', -8,True> ... ok
    test_is_even__<'Foo', -sys.maxsize> ... ok
    test_is_even__<'Foo', 0,expected=True> ... ok
    test_is_even__<'Foo', 15,expected=False> ... ok
    test_is_even__<'Foo', 17,expected=False> ... ok
    test_is_even__<'Foo', 18 -> True> ... ok
    test_is_even__<'Foo', 2,True> ... ok
    test_is_even__<'Foo', <12399999999...>,False> ... ok
    test_is_even__<'Foo', > ... ok
    test_is_even__<'Foo', >__2 ... ok
    test_is_even__<'Foo', expected=True,n=<12399999999...>> ... ok
    test_is_even__<'Foo', horribleabuse> ... ok
    test_is_even__<'Foo', noninteger> ... ok
    test_is_even__<'Foo', sys.maxsize> ... ok
    ...Ran 18 tests...
    OK

    >>> debug = []
    >>> parameters = paramseq(
    ...     1, 2, 3,
    ... ).context(debug_cm)
    >>>
    >>> @expand
    ... class Test:  # it is an old-style class if Python 2 is in use
    ...     @foreach(parameters)
    ...     def test(self, n):
    ...         debug.append(n)
    ...
    >>> # confirming that unittest_expander machinery acted properly:
    >>> instance = Test()
    >>> type(instance.test) is Substitute
    True
    >>> t1 = getattr(instance, 'test__<1>')
    >>> t2 = getattr(instance, 'test__<2>')
    >>> t3 = getattr(instance, 'test__<3>')
    >>> t1()
    >>> t2()
    >>> t3()
    >>> debug == [
    ...     'enter', 1, 'exit',
    ...     'enter', 2, 'exit',
    ...     'enter', 3, 'exit',
    ... ]
    True

    >>> debug = []
    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach([
    ...         param(),
    ...     ])
    ...     def test(self, **kwargs):
    ...         # **kwargs means accepting `label` and `context_targets`
    ...         debug.append(sorted(kwargs.keys()))
    ...
    >>> run_tests(Test)              # doctest: +ELLIPSIS
    test__<> ... ok
    ...Ran 1 test...
    OK
    >>> debug == [
    ...     ['context_targets', 'label'],
    ... ]
    True
    >>> type(Test.test) is Substitute
    True

    >>> import sys
    >>> no_qn = not _PY3
    >>> no_qn or getattr(Test, 'test__<>').__qualname__ == 'Test.test__<>'
    True

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach([
    ...         param(),
    ...     ])
    ...     def test(self):
    ...         pass
    ...
    ...     test.__qualname__ = 'Test.test_foo'
    ...
    >>> no_qn or getattr(Test, 'test__<>').__qualname__ == '<...>.test__<>'
    True

    >>> @expand
    ... class Test(unittest.TestCase):
    ...
    ...     # (param collection containing 1 empty tuple)
    ...     @foreach([()])
    ...     def test(self, label, context_targets):
    ...         self.assertEqual(label, '')
    ...         self.assertEqual(context_targets, [])
    ...
    ...     # (param collection containing 1 empty param object, with label)
    ...     @foreach([param().label('spam')])
    ...     def test_another(self, **kwargs):
    ...         self.assertEqual(kwargs['label'], 'spam')
    ...         self.assertEqual(kwargs['context_targets'], [])
    ...
    >>> run_tests(Test)                  # doctest: +ELLIPSIS
    test__<> ... ok
    test_another__<spam> ... ok
    ...Ran 2 test...
    OK

    >>> @expand
    ... class TestWithEmptyParamCollections(unittest.TestCase):
    ...
    ...     @foreach()   # XXX: should cause warning or what...
    ...     def test(self):
    ...         assert False
    ...
    ...     @foreach([])   # XXX: should cause warning or what...
    ...     def test(self, label, context_targets):
    ...         assert False
    ...
    ...     @foreach(paramseq())   # XXX: should cause warning or what...
    ...     def test_another(self):
    ...         assert False
    ...
    ...     @foreach(paramseq([]))   # XXX: should cause warning or what...
    ...     def test_another(self, **kwargs):
    ...         assert False
    ...
    ...     @foreach()   # XXX: should cause warning or what...
    ...     @foreach(paramseq([1, 2, 3]))
    ...     def test_another(self):
    ...         assert False
    ...
    ...     @foreach(paramseq([1, 2, 3]))
    ...     @foreach(paramseq([]))   # XXX: should cause warning or what...
    ...     def test_another(self, label):
    ...         assert False
    ...
    >>> run_tests(TestWithEmptyParamCollections)           # doctest: +ELLIPSIS
    <BLANKLINE>
    ...Ran 0 test...
    OK

    >>> class Some(object): pass
    >>> not_a_method = Some()
    >>> @expand                      # doctest: +ELLIPSIS
    ... class Test(unittest.TestCase):
    ...     wrong = foreach([1, 2])(not_a_method)
    ...
    Traceback (most recent call last):
    TypeError: ...is not a...

    >>> expand(illegal_arg='spam')   # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...argument...

    >>> as_unbound_meth = (
    ...     (lambda func, _: func) if _PY3
    ...     else (lambda func, owner: types.MethodType(func, None, owner))
    ... )
    >>> class WeirdPseudoMetaclass(object):
    ...
    ...     def __init__(self):
    ...         class X: disregarded = '...whatever...'
    ...
    ...         class Y: xyz = '...whatever...'
    ...         setattr(Y, 'abc__<1>', '...whatever...')
    ...
    ...         class Z: irrelevant = '...whatever...'
    ...
    ...         self.__mro__ = (X, Y, Z)
    ...         self.__slots__ = ['xyz__<4>__2']
    ...
    ...         setattr(self, 'xyz__<4>', 42)
    ...
    ...         @foreach(1, 2)
    ...         def abc(): pass
    ...         self.abc = as_unbound_meth(abc, self)
    ...         # (^ 'abc' is in dir())
    ...
    ...         @foreach(3, 4)
    ...         def xyz(): pass
    ...         self.xyz = as_unbound_meth(xyz, self)
    ...         # (^ 'xyz' is in dir())
    ...
    ...         @foreach(7, 8)
    ...         def disregarded(): pass
    ...         self.disregarded = as_unbound_meth(disregarded, self)
    ...         # (^ 'disregarded' is *not* in dir())
    ...
    ...         @foreach(9, 10)
    ...         def another_disregarded(): pass
    ...         self.another_disregarded = as_unbound_meth(another_disregarded, self)
    ...         # (^ 'another_disregarded' is *not* in dir())
    ...
    ...     def __dir__(self):
    ...         return ['abc', 'xyz', 'qwerty', 'qwerty__<6>', 'nonexistent']
    ...
    ...     def __getattr__(self, name):
    ...         if name == 'qwerty__<5>':
    ...             return 'I am not in any namespace, but still appear present! :-)'
    ...         if name == 'nonexistent' or '__<' in name:
    ...             raise AttributeError('no way!')
    ...         assert name == 'qwerty', name
    ...         # ('qwerty' is only in dir(), *not* in __mro__ namespaces, __dict__ or __slots__)
    ...         @foreach(5, 6)
    ...         def zzz():
    ...             pass
    ...         return as_unbound_meth(zzz, self)
    ...
    >>> PseudoClass = WeirdPseudoMetaclass()
    >>> expand(PseudoClass) is PseudoClass
    True
    >>> if _PY3:
    ...     {name: (type(obj), getattr(obj, '__qualname__', None))
    ...      for name, obj in vars(PseudoClass).items()
    ...      if not name.startswith('_')
    ...     } == {
    ...         'abc': (
    ...             Substitute,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.abc',
    ...          ),
    ...         'abc__<1>__2': (   # (because 'abc__<1>' already in PseudoClass.__mro__ namespaces)
    ...             Function,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.abc__<1>__2',
    ...          ),
    ...         'abc__<2>': (
    ...             Function,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.abc__<2>',
    ...          ),
    ...         'xyz': (
    ...             Substitute,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.xyz',
    ...          ),
    ...         'xyz__<3>': (
    ...             Function,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.xyz__<3>',
    ...          ),
    ...         'xyz__<4>': (
    ...             int,
    ...             None,
    ...          ),
    ...         'xyz__<4>__3': (   # (because 'xyz__<4>' already in PseudoClass.__dict__
    ...             Function,      #  and 'xyz__<4>__2' already in PseudoClass.__slots__)
    ...             'WeirdPseudoMetaclass.__init__.<locals>.xyz__<4>__3',
    ...          ),
    ...         'qwerty': (
    ...             Substitute,
    ...             'WeirdPseudoMetaclass.__getattr__.<locals>.zzz',
    ...          ),
    ...         'qwerty__<5>__2': (   # (because hasattr(PseudoClass, 'qwerty__<5>') is true)
    ...             Function,
    ...             'WeirdPseudoMetaclass.__getattr__.<locals>.qwerty__<5>__2',
    ...          ),
    ...         'qwerty__<6>__2': (   # (because 'qwerty__<6>' already in dir(PseudoClass))
    ...             Function,
    ...             'WeirdPseudoMetaclass.__getattr__.<locals>.qwerty__<6>__2',
    ...          ),
    ...         'disregarded': (
    ...             Function,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.disregarded',
    ...          ),
    ...         'another_disregarded': (
    ...             Function,
    ...             'WeirdPseudoMetaclass.__init__.<locals>.another_disregarded',
    ...          ),
    ...     }
    ... else:
    ...     {name: type(obj)
    ...      for name, obj in vars(PseudoClass).items()
    ...      if not name.startswith('_')
    ...     } == {
    ...         'abc': Substitute,
    ...         'abc__<1>__2': Function,  # (because 'abc__<1>' in PseudoClass.__mro__ namespaces)
    ...         'abc__<2>': Function,
    ...         'xyz': Substitute,
    ...         'xyz__<3>': Function,
    ...         'xyz__<4>': int,
    ...         'xyz__<4>__3': Function,  # (because 'xyz__<4>' already in PseudoClass.__dict__
    ...         'qwerty': Substitute,     #  and 'xyz__<4>__2' already in PseudoClass.__slots__)
    ...         'qwerty__<5>__2': Function, # (because hasattr(PseudoClass, 'qwerty__<5>') is true)
    ...         'qwerty__<6>__2': Function,   # (because 'qwerty__<6>' already in dir(PseudoClass))
    ...         'disregarded': types.MethodType,
    ...         'another_disregarded': types.MethodType,
    ...     }
    True

    >>> @expand
    ... class TestWithWrongContext(unittest.TestCase):
    ...
    ...     @foreach([
    ...         # int does not implement the *context manager* protocol
    ...         param(foo='abc').context(int, '42'),
    ...     ])
    ...     def test(self, foo):
    ...         pass
    ...
    >>> run_tests(TestWithWrongContext)  # doctest: +ELLIPSIS
    test__<foo='abc'> ... ERROR
    ...
    Traceback (most recent call last):
      ...
    <EXCEPTION WHEN NOT-A-CONTEXT-MANAGER GIVEN>
    ...
    Ran 1 test...
    FAILED (errors=1)
"""

import sys

_PY3 = (sys.version_info[0] >= 3)
_PY3_11_OR_NEWER = (sys.version_info[:2] >= (3, 11))
_PY3_7_OR_OLDER = (sys.version_info[:2] <= (3, 7))

if _PY3:
    if _PY3_11_OR_NEWER:
        __doc__ = __doc__.replace(
            '<EXCEPTION WHEN NOT-A-CONTEXT-MANAGER GIVEN>',
            "TypeError: ...does not support the context manager protocol...")
    else:
        __doc__ = __doc__.replace(
            '<EXCEPTION WHEN NOT-A-CONTEXT-MANAGER GIVEN>',
            'AttributeError: ...__enter__...')

    __doc__ += """
    >>> @expand
    ... class Test_is_even(unittest.TestCase):
    ...
    ...     # (let's also cover test methods whose signatures include
    ...     # *various kinds of arguments* and *type annotations*...)
    ...
    ...     @foreach(
    ...         param(-14, expected=True),
    ...         param(-1, expected=False),
    ...         param(0, expected=True),
    ...         param(2, expected=True),
    ...         param(17, expected=False),
    ...     )
    ...     def test_is_even(self, n, *, expected, label):
    ...         actual = is_even(n)
    ...         self.assertTrue(isinstance(actual, bool))
    ...         self.assertEqual(actual, expected)
    ...         self.assertIsInstance(label, str)
    ...
    ...     @foreach(
    ...         param('X', 'Y', 1, 2, '345', n=42),
    ...         param('X', y='Y', n=42),
    ...         param('X', y='Y'),
    ...     )
    ...     def test_whatever(self, x: str, /, y: str, *args: object, n: int = 42, **kw) -> None:
    ...         self.assertEqual(x, 'X')
    ...         self.assertEqual(y, 'Y')
    ...         self.assertIn(args, [(), (1, 2, '345')])
    ...         self.assertEqual(n, 42)
    ...         self.assertTrue(set(_GENERIC_KWARGS).issubset(kw))
    ...
    ...     ## FIXME: *accepted generic kwargs* should not include
    ...     ##        names of detected positional-only parameters
    ...     # @foreach([param()])
    ...     # def test_xxx(self, label='tralala', /):
    ...     #     self.assertEqual(label, 'tralala')
    ...
    >>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
    test_is_even__<-1,expected=False> ... ok
    test_is_even__<-14,expected=True> ... ok
    test_is_even__<0,expected=True> ... ok
    test_is_even__<17,expected=False> ... ok
    test_is_even__<2,expected=True> ... ok
    test_whatever__<'X','Y',1,2,'345',n=42> ... ok
    test_whatever__<'X',n=42,y='Y'> ... ok
    test_whatever__<'X',y='Y'> ... ok
    ...Ran 8 tests...
    OK
    """
    if _PY3_7_OR_OLDER:
        __doc__ = __doc__.replace(
            'test_whatever(self, x: str, /, y: str, *args',
            'test_whatever(self, x: str, y: str, *args')
else:
    __doc__ = __doc__.replace(
        '<EXCEPTION WHEN NOT-A-CONTEXT-MANAGER GIVEN>',
        'AttributeError: ...__exit__...')


try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc
import functools
import inspect
import itertools
import string
import types
import warnings

__all__ = (
    'foreach',
    'expand',
    'param',
    'paramseq',
    'Substitute',
)

__version__ = '0.5.0.dev0'


_CLASS_TYPES = (type,) if _PY3 else (type, types.ClassType)
_TEXT_STRING_TYPES = (str,) if _PY3 else (str, unicode)

_PARAMSEQ_OBJS_ATTR = '__attached_paramseq_objs'

_GENERIC_KWARGS = 'context_targets', 'label'

_DEFAULT_PARAMETRIZED_NAME_PATTERN = '{base_name}__<{label}>'
_DEFAULT_PARAMETRIZED_NAME_FORMATTER = string.Formatter()


if _PY3:
    def _get_context_manager_enter_and_exit(cm):
        cm_type = type(cm)
        # for consistency with the `with` statement's behavior:
        if _PY3_11_OR_NEWER:
            # (see: https://github.com/python/cpython/issues/56231
            # and https://github.com/python/cpython/issues/88637)
            try:
                enter_func = cm_type.__enter__
                exit_func = cm_type.__exit__
            except AttributeError:                                      # XXX @Py3: `as exc`
                raise TypeError(
                    '{.__qualname__!r} object does not support the '
                    'context manager protocol'.format(cm_type))         # XXX @Py3: `from exc`
        else:
            enter_func = cm_type.__enter__
            exit_func = cm_type.__exit__
        # (make instance methods by binding the functions to the instance)
        enter = types.MethodType(enter_func, cm)
        exit = types.MethodType(exit_func, cm)
        return enter, exit
else:
    def _get_context_manager_enter_and_exit(cm):
        # for consistency with the `with` statement's behavior under
        # Python 2.7, *first* get __exit__, *then* get __enter__
        cm_type = type(cm)
        if cm_type is types.InstanceType:
            # (old-style class -> get from the instance)
            exit = cm.__exit__
            enter = cm.__enter__
        else:
            # (new-style class -> get from the class and bind to the instance)
            exit = types.MethodType(cm_type.__exit__.__func__, cm, cm_type)
            enter = types.MethodType(cm_type.__enter__.__func__, cm, cm_type)
        return enter, exit


class _DisabledExcSuppressContextManagerWrapper(object):

    def __init__(self, cm):
        self._enter, self._exit = _get_context_manager_enter_and_exit(cm)

    def __enter__(self):
        return self._enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._exit(exc_type, exc_val, exc_tb)
        return False  # exception is *never* suppressed


class _Context(object):

    def __init__(self, context_manager_factory, *args, **kwargs):
        self._context_manager_factory = context_manager_factory
        self._enable_exc_suppress = kwargs.pop(
            '_enable_exc_suppress_', False)
        self._args = args
        self._kwargs = kwargs

    def _make_context_manager(self):
        cm = self._context_manager_factory(*self._args, **self._kwargs)
        if self._enable_exc_suppress:
            return cm
        else:
            return _DisabledExcSuppressContextManagerWrapper(cm)


class Substitute(object):

    def __init__(self, actual_object):
        self.actual_object = actual_object

    def __getattribute__(self, name):
        if name in ('actual_object', '__class__', '__call__'):
            return super(Substitute, self).__getattribute__(name)
        return getattr(self.actual_object, name)

    def __dir__(self):
        names = ['actual_object']
        names.extend(
            name for name in dir(self.actual_object)
            if name not in ('actual_object', '__call__'))
        return names


class param(object):

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._context_list = []
        self._label_list = []

    def context(self, context_manager_factory, *args, **kwargs):
        ctx = _Context(context_manager_factory, *args, **kwargs)
        return self._clone_adding(context_list=[ctx])

    def label(self, text):
        return self._clone_adding(label_list=[text])

    @classmethod
    def _from_pseq_item(cls, pseq_item):
        if isinstance(pseq_item, param):
            return pseq_item
        if isinstance(pseq_item, tuple):
            return cls(*pseq_item)
        return cls(pseq_item)

    @classmethod
    def _combine_instances(cls, param_instances):
        combined_args = []
        combined_kwargs = {}
        joined_label_list = []
        all_context_lists = []
        for param_inst in param_instances:
            assert isinstance(param_inst, param)
            combined_args.extend(param_inst._args)
            cls._verify_no_conflicting_kwargs(combined_kwargs, param_inst._kwargs)
            combined_kwargs.update(param_inst._kwargs)
            joined_label_list.append(param_inst._get_joined_label())
            all_context_lists.append(param_inst._context_list)
        return cls(*combined_args, **combined_kwargs)._clone_adding(
            label_list=joined_label_list,
            context_list=cls._get_combined_context_list(all_context_lists))

    @staticmethod
    def _verify_no_conflicting_kwargs(kwargs1, kwargs2):
        conflicting = frozenset(kwargs1).intersection(kwargs2)
        if conflicting:
            raise ValueError(
                'conflicting keyword arguments: ' +
                ', '.join(sorted(map(repr, conflicting))))

    @staticmethod
    def _get_combined_context_list(all_context_lists):
        flag = expand.legacy_context_ordering
        if flag is None:
            warnings.warn(
                'XXX',
                DeprecationWarning,
                stacklevel=4)  ### XXX
        elif not isinstance(flag, bool):
            raise TypeError(
                '`expand.legacy_context_ordering` must be '
                'False, True or None (found: {!r})'.format(flag))
        elif not flag:
            all_context_lists.reverse()
        combined_context_list = [
            ctx
            for context_list in all_context_lists
                for ctx in context_list]
        return combined_context_list

    def _clone_adding(self, context_list=None, label_list=None):
        """
        >>> p = param(1, b=42)
        >>> p._context_list = ['x']
        >>> p._label_list=['v']
        >>> p._param__cached_cm_factory = 'something'
        >>> p2 = p._clone_adding()
        >>> p._args == p2._args == (1,)
        True
        >>> p._kwargs == p2._kwargs == {'b': 42}
        True
        >>> p._context_list == p2._context_list == ['x']
        True
        >>> p._label_list == p2._label_list == ['v']
        True

        >>> p3 = p._clone_adding(
        ...     context_list=['q', 'w'],
        ...     label_list=['t', 'y'])
        >>> p3._args == (1,)
        True
        >>> p3._kwargs == {'b': 42}
        True
        >>> p3._context_list == ['x', 'q', 'w']
        True
        >>> p3._label_list == ['v', 't', 'y']
        True

        >>> p._param__cached_cm_factory == 'something'
        True
        >>> hasattr(p2, '_param__cached_cm_factory')
        False
        >>> hasattr(p3, '_param__cached_cm_factory')
        False
        """
        new = self.__class__(*self._args, **self._kwargs)
        new._context_list.extend(self._context_list)
        new._label_list.extend(self._label_list)
        if context_list:
            new._context_list.extend(context_list)
        if label_list:
            new._label_list.extend(label_list)
        return new

    def _get_compound_context_manager_factory(self):
        try:
            return self.__cached_cm_factory
        except AttributeError:
            # we need to combine several context managers (from the
            # contexts), but in Py2.7 there is no contextlib.ExitStack,
            # and contextlib.nested() is deprecated (for good reasons)
            # -- so we will just generate and execute the code:
            src_code = (
                'import contextlib\n'
                '@contextlib.contextmanager\n'
                'def cm_factory(context_targets):\n'
                '    assert context_targets == []\n'
                '    {enclosing_withs}yield\n'.format(
                    # (note: if self._context_list is empty,
                    # enclosing_withs will be an empty string)
                    enclosing_withs=''.join(
                        ('with context_list[{0}]._make_context_manager() '
                         'as ctx_target:\n'
                         '{next_indent}context_targets.append(ctx_target)\n'
                         '{next_indent}'
                        ).format(i, next_indent=((8 + 4 * i) * ' '))
                        for i in range(len(self._context_list)))))
            # Py2+Py3-compatible substitute of exec in a given namespace
            code = compile(src_code, '<string>', 'exec')
            namespace = {'context_list': self._context_list}
            eval(code, namespace)
            self.__cached_cm_factory = namespace['cm_factory']
            return self.__cached_cm_factory

    def _get_joined_label(self):
        if self._label_list:
            return ', '.join(self._label_list)
            #return ', '.join(filter(bool, self._label_list))  # XXX: later...
        else:
            short_repr = self._short_repr
            args_reprs = (short_repr(val) for val in self._args)
            kwargs_reprs = ('{}={}'.format(key, short_repr(val))
                            for key, val in sorted(self._kwargs.items()))
            return ','.join(itertools.chain(args_reprs, kwargs_reprs))

    @staticmethod
    def _short_repr(obj, max_len=16):  # XXX: improve this...
        r = repr(obj)
        if len(r) > max_len:
            r = '<{}...>'.format(r.lstrip('<')[:max_len-5])
        return r


class paramseq(object):

    def __new__(*cls_and_args, **kwargs):                               # noqa
        cls = cls_and_args[0]
        args = cls_and_args[1:]
        if len(args) == 1 and not kwargs:
            [param_col] = args
            if type(param_col) is cls:
                # the sole positional argument is a ready paramseq
                # object, so let's just return it
                return param_col
            # the sole positional argument is a parameter collection --
            # its items are parameter values or tuples of such values
            # (to be coerced to param instances), or just ready param
            # instances
            new = cls._make_new_wrapping_param_collections(param_col)
        else:
            # each value in args/kwargs is a parameter value or a tuple
            # of such values (to be coerced to a `param` instance), or
            # just a ready param instance; in the case of kwargs each of
            # them will be additionally .label()-ed with the respective
            # key, i.e., the argument name (see: _generate_raw_params())
            new = cls._make_new_wrapping_param_collections(list(args), kwargs)
        return new

    def __add__(self, other):
        if self._is_legal_param_collection(other):
            return self._make_new_wrapping_param_collections(self, other)
        return NotImplemented

    def __radd__(self, other):
        if self._is_legal_param_collection(other):
            return self._make_new_wrapping_param_collections(other, self)
        return NotImplemented

    def context(self, context_manager_factory, *args, **kwargs):
        ctx = _Context(context_manager_factory, *args, **kwargs)
        new = self._make_new_wrapping_param_collections(self)
        new._context_list.append(ctx)                                   # noqa
        return new

    @classmethod
    def _make_new_wrapping_param_collections(cls, *param_collections):
        cls._verify_param_collections_are_legal(param_collections)
        new = super(paramseq, cls).__new__(cls)
        new._param_collections = param_collections
        new._context_list = []
        return new

    @classmethod
    def _verify_param_collections_are_legal(cls, param_collections):
        for param_col in param_collections:
            if not cls._is_legal_param_collection(param_col):
                raise TypeError(
                    '{!r} is not a legal parameter '
                    'collection'.format(param_col))

    @staticmethod
    def _is_legal_param_collection(obj):
        return (
            isinstance(obj, (
                paramseq,
                collections_abc.Sequence,
                collections_abc.Set,
                collections_abc.Mapping)
            ) and
            not isinstance(obj, (
                tuple,
                _TEXT_STRING_TYPES,
                bytes,
                bytearray)
            )
        ) or callable(obj)

    def _generate_params(self, test_cls):
        for param_inst in self._generate_raw_params(test_cls):
            assert isinstance(param_inst, param)
            if self._context_list:                                             # noqa
                param_inst = param_inst._clone_adding(                         # noqa
                    context_list=self._context_list)                           # noqa
            yield param_inst

    def _generate_raw_params(self, test_cls):
        for param_col in self._param_collections:                              # noqa
            if isinstance(param_col, paramseq):
                for param_inst in param_col._generate_params(test_cls):
                    yield param_inst
            elif isinstance(param_col, collections_abc.Mapping):
                for label, pseq_item in param_col.items():
                    yield param._from_pseq_item(pseq_item).label(label)        # noqa
            else:
                if callable(param_col):
                    param_col = self._param_collection_callable_to_iterable(
                        param_col,
                        test_cls)
                else:
                    assert isinstance(param_col, (collections_abc.Sequence,
                                                  collections_abc.Set))
                for pseq_item in param_col:
                    yield param._from_pseq_item(pseq_item)                     # noqa

    @staticmethod
    def _param_collection_callable_to_iterable(param_col, test_cls):
        try:
            return param_col(test_cls)
        except TypeError:
            return param_col()


# test *method* decorator...
def foreach(*args, **kwargs):
    pseq = paramseq(*args, **kwargs)                                           # noqa

    def decorator(base_func):
        if not isinstance(base_func, types.FunctionType):
            raise TypeError(
                '{!r} is not a function (only functions can be '
                'decorated with @foreach...)'.format(base_func))
        _mark_test_method(base_func, pseq)
        return base_func

    return decorator


# test *class* decorator...
def expand(test_cls=None):
    if test_cls is None:
        return functools.partial(expand)
    _expand_test_methods(test_cls)
    return test_cls

expand.global_name_pattern = None
expand.global_name_formatter = None

expand.legacy_context_ordering = None
expand.legacy_signature_introspection = None


def _mark_test_method(base_func, pseq):
    stored_paramseq_objs = _get_paramseq_objs_or_none(base_func)
    if stored_paramseq_objs is None:
        stored_paramseq_objs = []
        setattr(base_func, _PARAMSEQ_OBJS_ATTR, stored_paramseq_objs)
    stored_paramseq_objs.append(pseq)


def _expand_test_methods(test_cls):
    dir_names = frozenset(_generate_dir_names(test_cls))
    initially_seen_names = frozenset(_generate_initially_seen_names(
        test_cls,
        dir_names))
    seen_names = set(initially_seen_names)
    (to_be_substituted,
     to_be_added) = _get_attrs_to_substitute_and_add(
        test_cls,
        dir_names,
        seen_names)
    assert dir_names <= initially_seen_names <= seen_names
    assert set(to_be_substituted) <= dir_names
    assert set(to_be_added).isdisjoint(initially_seen_names)
    assert set(to_be_added) <= seen_names
    for base_name, obj in to_be_substituted.items():
        setattr(test_cls, base_name, Substitute(obj))
    for func_name, func in to_be_added.items():
        setattr(test_cls, func_name, func)


def _generate_dir_names(test_cls):
    for name in dir(test_cls):
        if isinstance(name, str):  # (<- just in case...)
            yield name


def _generate_initially_seen_names(test_cls, dir_names):
    # note: we are extremely cautious with our policy of avoiding any
    # name clashes (see also: _may_name_be_already_taken()...)
    for name in dir_names:
        yield name
    # (typically, adding test_cls is redundant, as __mro__ should
    # already include it, but let's do it anyway -- just in case...)
    namespaces = (test_cls,) + getattr(test_cls, '__mro__', ())
    for spec_attr in ('__dict__', '__slots__'):
        for cls in namespaces:
            for name in getattr(cls, spec_attr, ()):
                if isinstance(name, str):  # (<- just in case...)
                    yield name


def _get_attrs_to_substitute_and_add(test_cls, dir_names, seen_names):
    to_be_substituted = dict()
    to_be_added = dict()
    for base_name in sorted(dir_names):
        obj = getattr(test_cls, base_name, None)
        if isinstance(obj, Substitute):
            continue
        stored_paramseq_objs = _get_paramseq_objs_or_none(obj)
        if stored_paramseq_objs is None:
            continue
        base_func = _get_base_func(obj)
        accepted_generic_kwargs = _get_accepted_generic_kwargs(base_func)
        for func in _generate_parametrized_functions(
                test_cls, stored_paramseq_objs,
                base_name, base_func, seen_names,
                accepted_generic_kwargs):
            assert func.__name__ not in to_be_added
            to_be_added[func.__name__] = func
        to_be_substituted[base_name] = obj
    return to_be_substituted, to_be_added


def _get_paramseq_objs_or_none(obj):
    paramseq_objs = getattr(obj, _PARAMSEQ_OBJS_ATTR, None)
    if paramseq_objs is None:
        return None
    if not isinstance(paramseq_objs, list):
        raise TypeError('{!r} is not a list'.format(paramseq_objs))
    if not all(isinstance(pseq, paramseq) for pseq in paramseq_objs):
        raise TypeError(
            '{!r} contains some items that are not '
            'paramseq objects'.format(paramseq_objs))
    return paramseq_objs


if _PY3:
    def _get_base_func(obj):
        # no unbound methods in Python 3
        if not isinstance(obj, types.FunctionType):
            raise TypeError('{!r} is not a function'.format(obj))
        return obj

    def _get_accepted_generic_kwargs(base_func):
        spec = inspect.getfullargspec(base_func)
        accepted_generic_kwargs = set(
            _GENERIC_KWARGS if spec.varkw is not None
            else (kw for kw in _GENERIC_KWARGS
                  if kw in (spec.args + spec.kwonlyargs)))
        return accepted_generic_kwargs

else:
    def _get_base_func(obj):
        if not isinstance(obj, types.MethodType):
            raise TypeError('{!r} is not a method'.format(obj))
        return obj.__func__

    def _get_accepted_generic_kwargs(base_func):
        spec = inspect.getargspec(base_func)
        accepted_generic_kwargs = set(
            _GENERIC_KWARGS if spec.keywords is not None
            else (kw for kw in _GENERIC_KWARGS
                  if kw in spec.args))
        return accepted_generic_kwargs


def _generate_parametrized_functions(test_cls, paramseq_objs,
                                     base_name, base_func,
                                     seen_names, accepted_generic_kwargs):
    src_params_iterables = [
        pseq._generate_params(test_cls)                                 # noqa
        for pseq in paramseq_objs]
    for count, params_row in enumerate(
            itertools.product(*src_params_iterables),
            start=1):
        combined_param_inst = param._combine_instances(params_row)      # noqa
        yield _make_parametrized_func(test_cls, base_name, base_func,
                                      seen_names, accepted_generic_kwargs,
                                      count, combined_param_inst)


def _make_parametrized_func(test_cls, base_name, base_func,
                            seen_names, accepted_generic_kwargs,
                            count, param_inst):
    p_args = param_inst._args                                           # noqa
    p_kwargs = param_inst._kwargs                                       # noqa
    label = param_inst._get_joined_label()                              # noqa
    cm_factory = param_inst._get_compound_context_manager_factory()     # noqa

    # XXX: analyze+fix/improve ad __dict__, __annotations__, __wrapped__,
    #      __signature__, __qualname__... + also set __module__
    @functools.wraps(base_func)
    def func(*args, **kwargs):
        args = list(args)
        args.extend(p_args)
        kwargs.update(p_kwargs)
        context_targets = []
        with cm_factory(context_targets):
            if 'context_targets' in accepted_generic_kwargs:
                kwargs.setdefault('context_targets', context_targets)
            if 'label' in accepted_generic_kwargs:
                kwargs.setdefault('label', label)
            return base_func(*args, **kwargs)

    delattr(func, _PARAMSEQ_OBJS_ATTR)
    _set_name(func, test_cls, base_name, base_func, label, count, seen_names)
    _set_qualname(func, test_cls, base_func)
    return func


def _set_name(func, test_cls, base_name, base_func, label, count, seen_names):
    pattern, formatter = _get_name_pattern_and_formatter()
    name = stem_name = formatter.format(
        pattern,
        base_name=base_name,
        base_obj=base_func,
        label=label,
        count=count)
    uniq_tag = 2
    while _may_name_be_already_taken(name, test_cls, seen_names):
        # ensure that, within this test class, the name will be unique
        name = '{}__{}'.format(stem_name, uniq_tag)
        uniq_tag += 1
    assert name not in seen_names
    seen_names.add(name)
    func.__name__ = name


def _get_name_pattern_and_formatter():
    pattern = getattr(expand, 'global_name_pattern', None)
    if pattern is None:
        pattern = _DEFAULT_PARAMETRIZED_NAME_PATTERN
    formatter = getattr(expand, 'global_name_formatter', None)
    if formatter is None:
        formatter = _DEFAULT_PARAMETRIZED_NAME_FORMATTER
    return pattern, formatter


def _may_name_be_already_taken(name, test_cls, seen_names):
    if name in seen_names:
        return True
    if hasattr(test_cls, name):
        seen_names.add(name)
        return True
    return False


# XXX: fix this later (by using test_cls...)
def _set_qualname(func, test_cls, base_func):
    # relevant to Python 3
    base_qualname = getattr(base_func, '__qualname__', None)
    if base_qualname is not None:
        base_name = base_func.__name__
        qualname_prefix = (
            base_qualname[:(len(base_qualname) - len(base_name))]
            if (base_qualname == base_name or
                base_qualname.endswith('.' + base_name))
            else '<...>.')
        func.__qualname__ = qualname_prefix + func.__name__
