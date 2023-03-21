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

As you see, it's fairly simple: you attach parameter collections to your
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

   Parameter collections -- such as *sequences* (e.g., :class:`list`
   instances), *mappings* (e.g., :class:`dict` instances), *sets*
   (e.g., :class:`set` or :class:`frozenset` instances) or just ready
   :class:`paramseq` instances -- do not need to be created or bound
   within the test class body; you could, for example, import them from
   a separate module. Obviously, that makes data/code reuse and
   refactorization easier.

   Also, note that the signatures of the :func:`foreach` decorator and
   the :class:`paramseq`'s constructor are identical: you pass in either
   exactly one positional argument which is a parameter collection or
   several (more than one) positional and/or keyword arguments being
   singular parameter values or tuples of parameter values, or
   :class:`param` instances.

.. note::

   We said that a parameter collection can be a *sequence* (among
   others; see the note above).  To be more precise: it can be a
   *sequence*, except that it *cannot be a text string* (:class:`str`
   in Python 3, :class:`str` or :class:`unicode` in Python 2).

.. warning::

   Also, a parameter collection should *not* be a tuple (i.e., an
   instance of the built-in type :class:`tuple` or, obviously, of any
   subclass of it, e.g., a *named tuple*), as this is **deprecated**
   and will become **illegal** in the *0.5.0* version of
   *unittest_expander*.

   Note that this deprecation concerns tuples used as *parameter
   collections*, *not* as *items* of parameter collections (tuples being
   such items, acting as simple substitutes of :class:`param` objects,
   are -- and will always be -- perfectly OK).

.. warning::

   Also, a parameter collection should *not* be a Python 3 *binary
   string-like sequence* (:class:`bytes` or :class:`bytearray`), as this
   is **deprecated** and will become **illegal** in the *0.5.0* version
   of *unittest_expander*.

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
directly to :func:`foreach`) can accept either no arguments or one
positional argument -- in the latter case the *test class* will be
passed in.

.. note::

   The callable object will be called -- and its *iterable* result will
   be iterated over (consumed) -- *when* the :func:`expand` decorator
   is being executed, *before* generating parametrized test methods.

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
...     data_with_contexts = [
...         param(save='', load='').context(NamedTemporaryFile, 'w+t'),
...         param(save='abc', load='abc').context(NamedTemporaryFile, 'w+t'),
...     ]
...
...     @foreach(data_with_contexts)
...     def test_save_load(self, save, load, context_targets):
...         file = context_targets[0]
...         file.write(save)
...         file.flush()
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...
...     # reusing the same params to show that a *new* context manager
...     # instance is created for each test call:
...     @foreach(data_with_contexts)
...     def test_save_load_with_spaces(self, save, load, context_targets):
...         file = context_targets[0]
...         file.write(' ' + save + ' ')
...         file.flush()
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
...         file.flush()
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
:meth:`__exit__` are properly called...) -- also when errors occur
(with some legitimate subtle reservations -- see:
:ref:`contexts-cannot-suppress-exceptions`):

>>> @contextlib.contextmanager
... def err_debug_cm(tag):
...     if tag.endswith('context-enter-error'):
...         debug.append('ERR-enter:' + tag)
...         raise RuntimeError('error in __enter__')
...     debug.append('enter:' + tag)
...     try:
...         yield tag
...         if tag.endswith('context-exit-error'):
...             raise RuntimeError('error in __exit__')
...     except:
...         debug.append('ERR-exit:' + tag)
...         raise
...     else:
...         debug.append('exit:' + tag)
...
>>> debug = []
>>> err_params = [
...     (
...         param().label('no_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner')
...     ),
...     (
...         param().label('test_fail')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner')
...     ),
...     (
...         param().label('test_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner')
...     ),
...     (
...         param().label('inner_context_enter_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner-context-enter-error')
...     ),
...     (
...         param().label('inner_context_exit_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner-context-exit-error')
...     ),
...     (
...         param().label('outer_context_enter_error')
...                .context(err_debug_cm, tag='outer-context-enter-error')
...                .context(err_debug_cm, tag='inner')
...     ),
...     (
...         param().label('outer_context_exit_error')
...                .context(err_debug_cm, tag='outer-context-exit-error')
...                .context(err_debug_cm, tag='inner')
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
...     'enter:outer',
...     'ERR-enter:inner-context-enter-error',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # inner_context_exit_error
...     'setUp',
...     'enter:outer',
...     'enter:inner-context-exit-error',
...     'test',
...     'ERR-exit:inner-context-exit-error',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # no_error
...     'setUp',
...     'enter:outer',
...     'enter:inner',
...     'test',
...     'exit:inner',
...     'exit:outer',
...     'tearDown',
...
...     # outer_context_enter_error
...     'setUp',
...     'ERR-enter:outer-context-enter-error',
...     'tearDown',
...
...     # outer_context_exit_error
...     'setUp',
...     'enter:outer-context-exit-error',
...     'enter:inner',
...     'test',
...     'exit:inner',
...     'ERR-exit:outer-context-exit-error',
...     'tearDown',
...
...     # test_error
...     'setUp',
...     'enter:outer',
...     'enter:inner',
...     'ERROR-test',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...     'tearDown',
...
...     # test_fail
...     'setUp',
...     'enter:outer',
...     'enter:inner',
...     'FAIL-test',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...     'tearDown',
... ]
True

Note that contexts attached to test *method* params (in contrast to
those attached to test *class* params -- see below:
:ref:`foreach-as-class-decorator`) are handled *directly* before (by
running :meth:`__enter__`) and after (by running :meth:`__exit__`) a
given parametrized test method call, that is, *after* :meth:`setUp`
and *before* :meth:`tearDown` calls -- so :meth:`setUp` and
:meth:`tearDown` are unaffected by any errors related to those
contexts.

On the other hand, an error in :meth:`setUp` prevents a test from
being called -- then contexts are not touched at all:

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
...         file.flush()
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


.. _foreach-as-class-decorator:

Deprecated feature: :func:`foreach` as a class decorator
========================================================

.. warning::

   Here we describe a **deprecated** feature.

   Decorating a *class* with :func:`foreach` will become **unsupported**
   in the *0.5.0* version of *unittest_expander*.

   Another **deprecation**, strictly related to the above, is that the
   ``into`` keyword argument to :func:`expand` will become **illegal**
   in the *0.5.0* version of *unittest_expander*.

:func:`foreach` can be used not only as a test *method* decorator but
also as a test *class* decorator -- to generate parametrized test
*classes*.

That allows you to share each specified parameter/context/label across
all test methods.  Parameters (and labels, and context targets) are
accessible as instance attributes (*not* as method arguments) from any
test method, as well as from the :meth:`setUp` and :meth:`tearDown`
methods.

>>> params_with_contexts = paramseq(                          # 2 param items
...     param(save='', load=''),
...     param(save='abc', load='abc'),
... ).context(NamedTemporaryFile, 'w+t')
>>> useless_data = [                                          # 2 param items
...     param('foo', b=42),
...     param('foo', b=433)]
>>> 
>>> @expand(into=globals())  # note the 'into' keyword-only argument
... @foreach(params_with_contexts)
... @foreach(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...         assert self.save == self.load
...         assert self.params == ('foo',)  # self.params <- *positional* ones
...         assert self.b in (42, 433)
...         assert 'foo' in self.label
...
...     @foreach(param(suffix=' '), param(suffix='XX'))       # 2 param items
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in dir():  # doctest: +ELLIPSIS
...     if name.startswith('TestSaveLoad'):
...         name
...
'TestSaveLoad'
"TestSaveLoad__<'foo',b=42, load='',save=''>"
"TestSaveLoad__<'foo',b=42, load='abc',save='abc'>"
"TestSaveLoad__<'foo',b=433, load='',save=''>"
"TestSaveLoad__<'foo',b=433, load='abc',save='abc'>"
>>> 
>>> test_classes = [globals()[name] for name in dir()
...                 if name.startswith('TestSaveLoad__')]
>>> # (note: 2 * 2 * 2 param items -> 8 parametrized tests)
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__<suffix=' '> (..._<'foo',b=42, load='',save=''>...) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='',save=''>...) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=42, load='abc',save='abc'>...) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='abc',save='abc'>...) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='',save=''>...) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='',save=''>...) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='abc',save='abc'>...) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='abc',save='abc'>...) ... ok
...Ran 8 tests...
OK

As you see, you can combine :func:`foreach` as *class* decorator(s) with
:func:`foreach` as *method* decorator(s) -- you will obtain tests
parametrized with the Cartesian product of the involved parameter
collections.

*Important:* when using :func:`foreach` as a *class* decorator you must
remember to place :func:`expand` as the topmost (the outer) class
decorator (above all :func:`foreach` decorators).

The *into* keyword argument for the :func:`expand` decorator specifies
where the generated (parametrized) subclasses of the decorated test
case class should be placed; the attribute value should be either a
mapping (typically: the :func:`globals()` dictionary) or a
(non-read-only) Python module object, or a (possibly dotted) name of
such a module.

Below: an example with the *into* argument being a module object:

>>> import types
>>> module = types.ModuleType('_my_test_module')
>>> 
>>> @expand(into=module)
... @foreach(params_with_contexts)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     def test_save_load(self):
...         self.file.write(self.save)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load)
...
>>> for name in dir(module):
...     if not name.startswith('__'):
...         name  # doctest: +ELLIPSIS
...
"TestSaveLoad__<load='',save=''>"
"TestSaveLoad__<load='abc',save='abc'>"
>>> 
>>> TestSaveLoad__1 = getattr(module, "TestSaveLoad__<load='',save=''>")
>>> TestSaveLoad__2 = getattr(module, "TestSaveLoad__<load='abc',save='abc'>")
>>> 
>>> run_tests(TestSaveLoad__1, TestSaveLoad__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoad__<load='',save=''>...) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>...) ... ok
...Ran 2 tests...
OK

...and with *into* being an importable module name:

>>> module = types.ModuleType('_my_test_module')
>>> sys.modules['_my_test_module'] = module
>>> 
>>> @expand(into='_my_test_module')
... @foreach(params_with_contexts)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     def test_save_load(self):
...         self.file.write(self.save)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load)
...
>>> for name in dir(module):
...     if not name.startswith('__'):
...         name  # doctest: +ELLIPSIS
...
"TestSaveLoad__<load='',save=''>"
"TestSaveLoad__<load='abc',save='abc'>"
>>> 
>>> TestSaveLoad__1 = getattr(module, "TestSaveLoad__<load='',save=''>")
>>> TestSaveLoad__2 = getattr(module, "TestSaveLoad__<load='abc',save='abc'>")
>>> 
>>> run_tests(TestSaveLoad__1, TestSaveLoad__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoad__<load='',save=''>...) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>...) ... ok
...Ran 2 tests...
OK

...and with *into* not specified -- which has, generally, the same
effect as setting it to the :func:`globals` dictionary (however, this
implicit variant may not work with those Python implementations that do
not support stack frame introspection; *note:* CPython and PyPy do support
it perfectly ``:-)``):

.. doctest::
    :hide:

    >>> # magic needed only to run the next example in doctests environment
    >>> # -- just ignore it
    >>> __orig_expand = expand
    >>> def expand(test_cls):
    ...     global expand, __name__
    ...     try:
    ...         this = types.ModuleType('__my_weird_module')
    ...         sys.modules['__my_weird_module'] = this
    ...         orig_name = __name__
    ...         try:
    ...             __name__ = this.__name__
    ...             result = __orig_expand(test_cls)
    ...             globals().update(vars(this))
    ...             return result
    ...         finally:
    ...             __name__ = orig_name
    ...     finally:
    ...         expand = __orig_expand

>>> @expand
... @foreach(params_with_contexts)
... class TestSaveLoadIt(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     def test_save_load(self):
...         self.file.write(self.save)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load)
...
>>> for name in dir():
...     if name.startswith('TestSaveLoadIt'):
...         name
...
'TestSaveLoadIt'
"TestSaveLoadIt__<load='',save=''>"
"TestSaveLoadIt__<load='abc',save='abc'>"
>>> 
>>> TestSaveLoadIt__1 = globals()["TestSaveLoadIt__<load='',save=''>"]
>>> TestSaveLoadIt__2 = globals()["TestSaveLoadIt__<load='abc',save='abc'>"]
>>> 
>>> run_tests(TestSaveLoadIt__1, TestSaveLoadIt__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoadIt__<load='',save=''>...) ... ok
test_save_load (...TestSaveLoadIt__<load='abc',save='abc'>...) ... ok
...Ran 2 tests...
OK

Contexts are, obviously, properly handled -- also when errors occur
(with some legitimate subtle reservations -- see:
:ref:`contexts-cannot-suppress-exceptions`):

>>> debug = []             # see earlier definition of err_debug_cm()...
>>> err_params.extend([    # see earlier initialization of err_params...
...     (
...         param().label('setUp_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner')
...     ),
...     (
...         param().label('tearDown_error')
...                .context(err_debug_cm, tag='outer')
...                .context(err_debug_cm, tag='inner')
...     ),
... ])
>>> into_dict = {}  # this time we'll pass another mapping (not globals())
>>> 
>>> @expand(into=into_dict)
... @foreach(err_params)
... class SillyTest(unittest.TestCase):
...
...     def setUp(self):
...         if self.label == 'setUp_error':
...             debug.append('ERR-setUp')
...             raise RuntimeError
...         debug.append('setUp')
...
...     def tearDown(self):
...         if self.label == 'tearDown_error':
...             debug.append('ERR-tearDown')
...             raise RuntimeError
...         debug.append('tearDown')
...
...     def test(self):
...         if self.label == 'test_fail':
...             debug.append('FAIL-test')
...             self.fail()
...         elif self.label == 'test_error':
...             debug.append('ERROR-test')
...             raise RuntimeError
...         else:
...             debug.append('test')
...
>>> for name in sorted(into_dict):
...     name
...
'SillyTest__<inner_context_enter_error>'
'SillyTest__<inner_context_exit_error>'
'SillyTest__<no_error>'
'SillyTest__<outer_context_enter_error>'
'SillyTest__<outer_context_exit_error>'
'SillyTest__<setUp_error>'
'SillyTest__<tearDown_error>'
'SillyTest__<test_error>'
'SillyTest__<test_fail>'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test (...SillyTest__<inner_context_enter_error>...) ... ERROR
test (...SillyTest__<inner_context_exit_error>...) ... ERROR
test (...SillyTest__<no_error>...) ... ok
test (...SillyTest__<outer_context_enter_error>...) ... ERROR
test (...SillyTest__<outer_context_exit_error>...) ... ERROR
test (...SillyTest__<setUp_error>...) ... ERROR
test (...SillyTest__<tearDown_error>...) ... ERROR
test (...SillyTest__<test_error>...) ... ERROR
test (...SillyTest__<test_fail>...) ... FAIL
...Ran 9 tests...
FAILED (failures=1, errors=7)
>>> debug == [
...     # inner_context_enter_error
...     'enter:outer',
...     'ERR-enter:inner-context-enter-error',
...     'ERR-exit:outer',
...
...     # inner_context_exit_error
...     'enter:outer',
...     'enter:inner-context-exit-error',
...     'setUp',
...     'test',
...     'tearDown',
...     'ERR-exit:inner-context-exit-error',
...     'ERR-exit:outer',
...
...     # no_error
...     'enter:outer',
...     'enter:inner',
...     'setUp',
...     'test',
...     'tearDown',
...     'exit:inner',
...     'exit:outer',
...
...     # outer_context_enter_error
...     'ERR-enter:outer-context-enter-error',
...
...     # outer_context_exit_error
...     'enter:outer-context-exit-error',
...     'enter:inner',
...     'setUp',
...     'test',
...     'tearDown',
...     'exit:inner',
...     'ERR-exit:outer-context-exit-error',
...
...     # setUp_error
...     'enter:outer',
...     'enter:inner',
...     'ERR-setUp',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...
...     # tearDown_error
...     'enter:outer',
...     'enter:inner',
...     'setUp',
...     'test',
...     'ERR-tearDown',
...     'ERR-exit:inner',
...     'ERR-exit:outer',
...
...     # test_error
...     'enter:outer',
...     'enter:inner',
...     'setUp',
...     'ERROR-test',  # note:
...     'tearDown',    # *not* ERR-tearDown
...     'exit:inner',  # *not* ERR-exit:inner
...     'exit:outer',  # *not* ERR-exit:outer
...
...     # test_fail
...     'enter:outer',
...     'enter:inner',
...     'setUp',
...     'FAIL-test',   # note:
...     'tearDown',    # *not* ERR-tearDown
...     'exit:inner',  # *not* ERR-exit:inner
...     'exit:outer',  # *not* ERR-exit:outer
... ]
True

Note that contexts attached to test *class* params (in contrast to
those attached to test *method* params -- see: :ref:`context-basics`)
are automatically handled within :meth:`setUp` and (if applicable)
:meth:`tearDown` -- so :meth:`setUp` and :meth:`tearDown` *are*
affected by errors related to those contexts.  On the other hand,
context finalization is *not* affected by any exceptions from actual
test methods (i.e., context managers' :meth:`__exit__` methods are
called with ``None, None, None`` arguments anyway -- unless
:meth:`setUp`/:meth:`tearDown` or an enclosed context manager's
:meth:`__enter__`/:meth:`__exit__` raises an exception).


Additional note about extending :meth:`setUp` and :meth:`tearDown`
------------------------------------------------------------------

.. warning::

   Here we refer to applying the :func:`foreach` decorator to a *class*
   which is a **deprecated** feature (see the warning at the beginning
   of the :ref:`foreach-as-class-decorator` section).

As you can see in the above examples, you can, without any problem,
implement your own :meth:`setUp` and/or :meth:`tearDown` methods in test
classes that are decorated with :func:`foreach` and :func:`expand`; the
*unittest_expander* machinery, which provides its own version of these
methods, will incorporate your implementations automatically -- by
obtaining them with :func:`super` and calling (*within* the scope of
any contexts that have been attached to your parameters with
:meth:`param.context` or :meth:`paramseq.context`).

However, if you need to create a subclass of one of the test classes
generated by :func:`expand` applied to a class decorated with
:func:`foreach` -- you need to obey the following rules:

* you shall not apply :func:`foreach` to that subclass or any class
  that inherits from it (though you can still apply :func:`foreach` to
  methods of the subclass);

* when extending :meth:`setUp` and/or :meth:`tearDown` methods:

  * in :meth:`setUp`, calling :meth:`setUp` of the superclass should be
    the first action;
  * in :meth:`tearDown`, calling :meth:`tearDown` of the superclass
    should be the last action -- and you shall ensure (by using a
    ``finally`` clause) that this action is *always* executed.

For example:

>>> # the SillyTest__<no_error> class from the previous code snippet
>>> base = into_dict['SillyTest__<no_error>']
>>> 
>>> class SillyTestSubclass(base):
...
...     def setUp(self):
...         debug.append('*** before everything ***')
...         # <- at this point no contexts are active (and there are
...         # no self.params, self.label, self.context_targets, etc.)
...         super(SillyTestSubclass, self).setUp()
...         # *HERE* is the place for your extension's implementation
...         debug.append('*** SillyTestSubclass.setUp ***')
...         assert hasattr(self, 'params')
...         assert hasattr(self, 'label')
...         assert hasattr(self, 'context_targets')
...
...     def tearDown(self):
...         try:
...             # *HERE* is the place for your extension's implementation
...             debug.append('*** SillyTestSubclass.tearDown ***')
...         finally:
...             super(SillyTestSubclass, self).tearDown()
...             # <- at this point no contexts are active
...         debug.append('*** after everything ***')
...
>>> debug = []
>>> run_tests(SillyTestSubclass)  # doctest: +ELLIPSIS
test (...SillyTestSubclass...) ... ok
...Ran 1 test...
OK
>>> debug == [
...     '*** before everything ***',
...     'enter:outer',
...     'enter:inner',
...     'setUp',
...     '*** SillyTestSubclass.setUp ***',
...     'test',
...     '*** SillyTestSubclass.tearDown ***',
...     'tearDown',
...     'exit:inner',
...     'exit:outer',
...     '*** after everything ***',
... ]
True


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
behavior is that suppressing exceptions is generally not a good idea
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
>>> into_dict = {}
>>> @expand(into=into_dict)
... @foreach([
...     param(setup_error=OSError)
...         .context(SillySuppressingCM, _enable_exc_suppress_=True),
...     param(setup_error=OSError)
...         .context(SillySuppressingCM, _enable_exc_suppress_=True)
...         .context(ErrorCM, error=TypeError),
...     param(setup_error=None),
... ])
... class AnotherSillyExcTest(unittest.TestCase):
...
...     def setUp(self):
...         if self.setup_error is not None:
...             debug.append('raising {}'.format(self.setup_error.__name__))
...             raise self.setup_error('ooops!')
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM, _enable_exc_suppress_=True)
...             .context(ErrorCM, error=RuntimeError),
...     ])
...     def test_it(self, test_error):
...         debug.append('raising {}'.format(test_error.__name__))
...         raise test_error('ha!')
...
>>> debug = []
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
test_it__... ok
...Ran 6 tests...
OK
>>> debug == [
...     'raising OSError',
...     'suppressing OSError',
...     'raising AssertionError',
...     'suppressing AssertionError',
... 
...     'raising OSError',
...     'suppressing OSError',
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...     'suppressing RuntimeError',
... 
...     'raising OSError',
...     'replacing OSError with TypeError',
...     'suppressing TypeError',
...     'raising AssertionError',
...     'suppressing AssertionError',
... 
...     'raising OSError',
...     'replacing OSError with TypeError',
...     'suppressing TypeError',
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...     'suppressing RuntimeError',
... 
...     'raising AssertionError',
...     'suppressing AssertionError',
... 
...     'raising KeyError',
...     'replacing KeyError with RuntimeError',
...     'suppressing RuntimeError',
... ]
True

Normally -- without ``_enable_exc_suppress_=True`` -- exceptions
*are* propagated even when :meth:`__exit__` returns a *true* value:

>>> into_dict = {}
>>> @expand(into=into_dict)
... @foreach([
...     param(setup_error=OSError)
...         .context(SillySuppressingCM),
...     param(setup_error=OSError)
...         .context(SillySuppressingCM)
...         .context(ErrorCM, error=TypeError),
...     param(setup_error=None),
... ])
... class AnotherSillyExcTest2(unittest.TestCase):
...
...     def setUp(self):
...         if self.setup_error is not None:
...             raise self.setup_error('ooops!')
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=RuntimeError),
...     ])
...     def test_it(self, test_error):
...         raise test_error('ha!')
...
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... FAIL
test_it__... ERROR
...Ran 6 tests...
FAILED (failures=1, errors=5)

Note that ``_enable_exc_suppress_=True`` changes nothing when context
manager's :meth:`__exit__` returns a *false* value:

>>> into_dict = {}
>>> @expand(into=into_dict)
... @foreach([
...     param(setup_error=OSError)
...         .context(SillySuppressingCM),
...     param(setup_error=OSError)
...         .context(SillySuppressingCM)
...         .context(ErrorCM, error=TypeError,
...                  _enable_exc_suppress_=True),
...     param(setup_error=None),
... ])
... class AnotherSillyExcTest3(unittest.TestCase):
...
...     def setUp(self):
...         if self.setup_error is not None:
...             raise self.setup_error('ooops!')
...
...     @foreach([
...         param(test_error=AssertionError)
...             .context(SillySuppressingCM),
...         param(test_error=KeyError)
...             .context(SillySuppressingCM)
...             .context(ErrorCM, error=RuntimeError,
...                      _enable_exc_suppress_=True),
...     ])
...     def test_it(self, test_error):
...         raise test_error('ha!')
...
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... ERROR
test_it__... FAIL
test_it__... ERROR
...Ran 6 tests...
FAILED (failures=1, errors=5)


.. _about-substitute:

:class:`Substitute` objects
===========================

One could ask: "What does the :func:`expand` decorator do with the
original objects (classes or methods) decorated with :func:`foreach`?"

>>> @expand
... @foreach(useless_data)
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

>>> DummyTest                         # doctest: +ELLIPSIS
<...Substitute object at 0x...>
>>> DummyTest.actual_object           # doctest: +ELLIPSIS
<class '...DummyTest'>
>>> DummyTest.attr
[42]
>>> DummyTest.attr is DummyTest.actual_object.attr
True
>>> (set(dir(DummyTest.actual_object)) - {'__call__'}
...  ).issubset(dir(DummyTest))
True

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
non-callable proxy to the original class or method (preventing it from
being included by test loaders, but still keeping it available for
introspection, etc.).


.. _custom-name-formatting:

Custom method/class name formatting
===================================

If you don't like how parametrized test method/class names are generated
-- you can customize that globally by:

* setting :attr:`expand.global_name_pattern` to a :meth:`~str.format`-able
  pattern, making use of zero or more of the following replacement fields:

  * ``{base_name}`` -- the name of the original test method or test class,
  * ``{base_obj}`` -- the original test method (technically: function)
    or test class,
  * ``{label}`` -- the test label (automatically generated or
    explicitly specified with :meth:`param.label`),
  * ``{count}`` -- consecutive number (within a single application of
    :func:`@expand`) of the generated parametrized test method or test
    class;

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

>>> expand.global_name_pattern = '{base_name}__parametrized_{count}'
>>> 
>>> into_dict = {}
>>> 
>>> @expand(into=into_dict)
... @foreach(params_with_contexts)
... @foreach(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     @foreach(param(suffix=' '), param(suffix='XX'))
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
'TestSaveLoad__parametrized_1'
'TestSaveLoad__parametrized_2'
'TestSaveLoad__parametrized_3'
'TestSaveLoad__parametrized_4'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_1...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_1...) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_2...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_2...) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_3...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_3...) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_4...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_4...) ... ok
...Ran 8 tests...
OK

...or, let's say:

>>> import string
>>> class SillyFormatter(string.Formatter):
...     def format(self, format_string, *args, **kwargs):
...         label = kwargs['label']
...         if '42' in label:
...             return '!{}!'.format(label)
...         else:
...             result = super(SillyFormatter,
...                            self).format(format_string, *args, **kwargs)
...             if isinstance(kwargs['base_obj'], type):
...                 result = result.replace('_', '^')
...             return result
...
>>> expand.global_name_formatter = SillyFormatter()
>>> 
>>> into_dict = {}
>>> 
>>> @expand(into=into_dict)
... @foreach(params_with_contexts)
... @foreach(*useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     @foreach([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.flush()
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
"!'foo',b=42, load='',save=''!"
"!'foo',b=42, load='abc',save='abc'!"
'TestSaveLoad^^parametrized^3'
'TestSaveLoad^^parametrized^4'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__parametrized_1 (...!'foo',b=42, load='',save=''!...) ... ok
test_save_load__parametrized_2 (...!'foo',b=42, load='',save=''!...) ... ok
test_save_load__parametrized_1 (...!'foo',b=42, load='abc',save='abc'!...) ... ok
test_save_load__parametrized_2 (...!'foo',b=42, load='abc',save='abc'!...) ... ok
test_save_load__parametrized_1 (...TestSaveLoad^^parametrized^3...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad^^parametrized^3...) ... ok
test_save_load__parametrized_1 (...TestSaveLoad^^parametrized^4...) ... ok
test_save_load__parametrized_2 (...TestSaveLoad^^parametrized^4...) ... ok
...Ran 8 tests...
OK

Set those attributes to :obj:`None` to restore the default behavior:

>>> expand.global_name_pattern = None
>>> expand.global_name_formatter = None


.. _avoiding-name-clashes:

Name clashes avoided automatically
==================================

:func:`expand` tries to avoid name clashes: when it detects that a
newly generated name clashes with an existing one, it adds a suffix
to the new name.  E.g.:

>>> def setting_attrs(attr_dict):
...     def deco(cls):
...         for k, v in attr_dict.items():
...             setattr(cls, k, v)
...         return cls
...     return deco
...
>>> into_dict = {
...     "Test_is_even__<'foo',b=42>": ('spam', 'spam', 'spam'),
... }
>>> extra_attrs = {
...     'test_even__<4>': 'something',
...     'test_even__<4>__2': None,
... }
>>> 
>>> @expand(into=into_dict)
... @foreach(useless_data)
... @setting_attrs(extra_attrs)
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
>>> for name, obj in sorted(into_dict.items()):  # doctest: +ELLIPSIS
...     if obj != ('spam', 'spam', 'spam'):
...         name
...
"Test_is_even__<'foo',b=42>__2"
"Test_is_even__<'foo',b=433>"
>>> 
>>> test_classes = [into_dict[name] for name, obj in sorted(into_dict.items())
...                 if obj != ('spam', 'spam', 'spam')]
...
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_even__<-16> (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<0> (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<0>__2 (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<0>__3 (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<0>__4 (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<4>__3 (...Test_is_even__<'foo',b=42>__2...) ... ok
test_even__<-16> (...Test_is_even__<'foo',b=433>...) ... ok
test_even__<0> (...Test_is_even__<'foo',b=433>...) ... ok
test_even__<0>__2 (...Test_is_even__<'foo',b=433>...) ... ok
test_even__<0>__3 (...Test_is_even__<'foo',b=433>...) ... ok
test_even__<0>__4 (...Test_is_even__<'foo',b=433>...) ... ok
test_even__<4>__3 (...Test_is_even__<'foo',b=433>...) ... ok
...Ran 12 tests...
OK


Questions and answers about various details...
==============================================

"Can I omit :func:`expand` and then apply it to subclasses?"
------------------------------------------------------------

Yes, you can.  Please consider the following example:

>>> debug = []
>>> into_dict = {}
>>> 
>>> # see earlier definition of debug_cm()...
>>> class_params = paramseq(1, 2, 3).context(debug_cm, tag='C')
>>> method_params = paramseq(7, 8, 9).context(debug_cm, tag='M')
>>> 
>>> @foreach(class_params)
... class MyTestMixIn(object):
...
...     @foreach(method_params)
...     def test(self, y):
...         [x] = self.params
...         debug.append((x, y, self.n))
...
>>> @expand(into=into_dict)
... class TestActual(MyTestMixIn, unittest.TestCase):
...     n = 42
...
>>> @expand(into=into_dict)
... class TestYetAnother(MyTestMixIn, unittest.TestCase):
...     n = 12345
...
>>> for name in sorted(into_dict):
...     name
...
'TestActual__<1>'
'TestActual__<2>'
'TestActual__<3>'
'TestYetAnother__<1>'
'TestYetAnother__<2>'
'TestYetAnother__<3>'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test__<7> (...TestActual__<1>...) ... ok
test__<8> (...TestActual__<1>...) ... ok
test__<9> (...TestActual__<1>...) ... ok
test__<7> (...TestActual__<2>...) ... ok
test__<8> (...TestActual__<2>...) ... ok
test__<9> (...TestActual__<2>...) ... ok
test__<7> (...TestActual__<3>...) ... ok
test__<8> (...TestActual__<3>...) ... ok
test__<9> (...TestActual__<3>...) ... ok
test__<7> (...TestYetAnother__<1>...) ... ok
test__<8> (...TestYetAnother__<1>...) ... ok
test__<9> (...TestYetAnother__<1>...) ... ok
test__<7> (...TestYetAnother__<2>...) ... ok
test__<8> (...TestYetAnother__<2>...) ... ok
test__<9> (...TestYetAnother__<2>...) ... ok
test__<7> (...TestYetAnother__<3>...) ... ok
test__<8> (...TestYetAnother__<3>...) ... ok
test__<9> (...TestYetAnother__<3>...) ... ok
...Ran 18 tests...
OK
>>> (type(MyTestMixIn) is type and
...  inspect.isfunction(vars(MyTestMixIn)['test']))               # (not touched by @expand)
True
>>> type(TestActual) is type(TestYetAnother) is Substitute           # (replaced by @expand)
True
>>> type(vars(TestActual.actual_object)['test']) is Substitute       # (replaced by @expand)
True
>>> type(vars(TestYetAnother.actual_object)['test']) is Substitute   # (replaced by @expand)
True
>>> debug == [
...     'enter:C', 'enter:M', (1, 7, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (1, 8, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (1, 9, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 7, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 8, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 9, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 7, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 8, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 9, 42), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (1, 7, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (1, 8, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (1, 9, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 7, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 8, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (2, 9, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 7, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 8, 12345), 'exit:M', 'exit:C',
...     'enter:C', 'enter:M', (3, 9, 12345), 'exit:M', 'exit:C',
... ]
True

Note that, most probably, you should name such mix-in or "test template"
base classes in a way that will prevent the test loader you use from
including them; for the same reason, typically, it is better to avoid
making them subclasses of :class:`unittest.TestCase`.

A similar yet simpler example (*without* using :func:`foreach`
as a *test class decorator*, which -- :ref:`as stated earlier
<foreach-as-class-decorator>` -- is a deprecated feature):

>>> debug = []
>>> class MyTestMixIn(object):
...
...     @foreach(method_params)  # (see method_params defined earlier...)
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


"Can I :func:`expand` a subclass of an already :func:`expand`-ed class?"
------------------------------------------------------------------------

As long as you do *not* apply :func:`foreach` to test *classes* (but
only to test *methods*) -- *yes, you can* (in some of the past versions
of *unittest_expander* it was broken, but now it works perfectly):

>>> debug = []
>>> into_dict = {}
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

But things complicate when you apply :func:`foreach` to test *classes*.
For such cases the answer is: *do not try this at home*.  :ref:`As
it was said earlier <foreach-as-class-decorator>`, the parts of
*unittest_expander* related to applying :func:`foreach` to classes
are **deprecated** anyway.


"Do my test classes need to inherit from :class:`unittest.TestCase`?"
---------------------------------------------------------------------

No, it doesn't matter from the point of view of the
*unittest_expander* machinery.

>>> debug = []
>>> into_dict = {}
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

However, note that if you decorate your test class (and not only its
methods) with :func:`foreach`, the test running tools you use are
expected to call :meth:`setUp` and :meth:`tearDown` methods
appropriately -- as *unittest*'s test running machinery does (though
your test class does not need to implement these methods by itself).

.. warning::

   Here we refer to applying the :func:`foreach` decorator to a *class*
   which is a **deprecated** feature (see the warning at the beginning
   of the :ref:`foreach-as-class-decorator` section).

>>> debug = []
>>> into_dict = {}
>>> 
>>> @expand(into=into_dict)
... @foreach(parameters)
... class Test(object):  # not a unittest.TestCase subclass
...
...     def test(self):
...         assert len(self.params) == 1
...         n = self.params[0]
...         debug.append(n)
...
>>> # confirming that unittest_expander machinery acted properly:
>>> type(Test) is Substitute
True
>>> orig_cls = Test.actual_object
>>> type(orig_cls) is type
True
>>> orig_cls.__bases__ == (object,)
True
>>> orig_cls.__name__ == 'Test'
True
>>> not hasattr(orig_cls, 'setUp') and not hasattr(orig_cls, 'tearDown')
True
>>> cls1 = into_dict['Test__<1>']
>>> cls2 = into_dict['Test__<2>']
>>> cls3 = into_dict['Test__<3>']
>>> issubclass(cls1, orig_cls)
True
>>> issubclass(cls2, orig_cls)
True
>>> issubclass(cls3, orig_cls)
True
>>> hasattr(cls1, 'setUp') and hasattr(cls1, 'tearDown')
True
>>> hasattr(cls2, 'setUp') and hasattr(cls2, 'tearDown')
True
>>> hasattr(cls3, 'setUp') and hasattr(cls3, 'tearDown')
True
>>> instance1 = cls1()
>>> instance2 = cls2()
>>> instance3 = cls3()
>>> for inst in [instance1, instance2, instance3]:
...     # doing what any reasonable test runner should do
...     inst.setUp()
...     try: inst.test()
...     finally: inst.tearDown()
...
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

>>> into_dict = {}
>>> @expand(into=into_dict)
... class TestIt2(unittest.TestCase):
...
...     def test(self):
...         sys.stdout.write(' [DEBUG: OK] ')
...         sys.stdout.flush()
...
>>> run_tests(TestIt2)  # doctest: +ELLIPSIS
test ... [DEBUG: OK] ok
...Ran 1 test...
OK
>>> into_dict
{}


"To what objects can :func:`foreach` be applied?"
-------------------------------------------------

The :func:`foreach` decorator is designed to be applied *only*:

* to regular test methods (being instance methods, *not* static or class
  methods), that is, to functions being attributes of test (or test
  mix-in) classes;
* to test (or test mix-in) classes themselves

(however, note that -- :ref:`as noted earlier <foreach-as-class-decorator>`
-- the latter is a deprecated feature).

You should *not* apply the decorator to anything else (especially,
not to static or class methods).  If you do, the effect is undefined:
an exception or some other faulty/unexpected behavior may be observed
(immediately or, for example, when :func:`expand` is applied, or when
tests are run...).


.. doctest::
    :hide:

    Other checks
    ============

    For completeness, let's also check some other usage cases and
    error conditions...

    >>> isinstance(paramseq(), paramseq)
    True
    >>> isinstance(paramseq(1, 2), paramseq)
    True
    >>> isinstance(paramseq(1, two=2), paramseq)
    True
    >>> isinstance(paramseq([1, 2]), paramseq)
    True
    >>> isinstance(paramseq({1, 2}), paramseq)
    True
    >>> isinstance(paramseq(a=3, b=4), paramseq)
    True
    >>> isinstance(paramseq(paramseq([1, 2])), paramseq)
    True
    >>> isinstance(paramseq([1, 2]) + {3, 4} + [5, 6], paramseq)
    True
    >>> isinstance({3, 4} + paramseq([1, 2]) + [5, 6], paramseq)
    True

    >>> @expand()  # <- effectively, same as `@expand` without `()`
    ... class Test_is_even(unittest.TestCase):
    ...
    ...     # Note: here, among other things, we cover using tuples as
    ...     # parameter collections -- which is deprecated, but still
    ...     # legal in unitest_expander 0.4.x.
    ...
    ...     params1a = paramseq() + (
    ...         (-14, True),
    ...     )
    ...     params1b = (
    ...         (-1, False),
    ...     )
    ...     params1ab = params1a + params1b
    ...
    ...     params1c = (
    ...         (-8, True),
    ...     )
    ...     params1d = paramseq((
    ...         (-7, False),
    ...     ))
    ...     params1cd = params1c + params1d
    ...
    ...     params1 = params1ab + params1cd
    ...
    ...     params2 = (
    ...         (),
    ...         param(),
    ...         param(0, expected=True),
    ...         (2, True),
    ...         param(17, expected=False),
    ...     )
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
    ...     params6 = (
    ...         (12399999999999999, False),
    ...         param(n=12399999999999998, expected=True),
    ...     )
    ...
    ...     @foreach(params1 + params2 + params3 + params4 + params5 + params6)
    ...     @foreach(('Foo',))
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

    >>> paramseq([1, 2]) + 3         # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> 3 + paramseq([1, 2])         # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq('123')              # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> expand(illegal_arg='spam')   # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...unexpected keyword arguments...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach(42)   # <- single arg that is not a proper param collection
    ...     def test(self):
    ...         pass                 # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand(into=['badtype'])    # doctest: +ELLIPSIS
    ... @foreach(1, 2)
    ... class Test(unittest.TestCase):
    ...     pass
    ...
    Traceback (most recent call last):
    TypeError: ...resolved 'into' argument is not a mutable mapping...

    >>> class Some1(object): pass
    >>> not_a_method = Some1()
    >>> @expand                      # doctest: +ELLIPSIS
    ... class Test(unittest.TestCase):
    ...     wrong = foreach([1, 2])(not_a_method)
    ...
    Traceback (most recent call last):
    TypeError: ...is not a...

    >>> class Some2(object): __dir__ = lambda self: []
    >>> not_a_class = Some2()
    >>> expand(foreach([1, 2])(not_a_class)
    ... )  # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...is not a class...

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
    >>> no_qn = sys.version_info < (3, 3)
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

    >>> into_dict = {}
    >>> @expand(into=into_dict)
    ... @foreach([42])
    ... class Test(unittest.TestCase):
    ...     pass
    ...
    >>> no_qn or into_dict['Test__<42>'].__qualname__ == 'Test__<42>'
    True

    >>> @expand(into=into_dict)
    ... @foreach(42)   # <- single arg that is not a proper param collection
    ... class Test(unittest.TestCase):
    ...     pass       # doctest: +ELLIPSIS
    ...
    Traceback (most recent call last):
    TypeError: ...not a legal parameter collection...

    >>> @expand
    ... class Test(unittest.TestCase):
    ...
    ...     @foreach([123])
    ...     class TestNested(unittest.TestCase):
    ...         pass
    ...
    ...     @foreach([123])
    ...     class TestNested_another:  # (<- here we have an old-style class if Python 2.x is used)
    ...         pass
    ...
    >>> (isinstance(Test.TestNested, _CLASS_TYPES) and
    ...  issubclass(Test.TestNested, unittest.TestCase))
    True
    >>> isinstance(Test.TestNested_another, _CLASS_TYPES)
    True
    >>> sorted(k for k in vars(Test).keys() if not k.startswith('_'))
    ['TestNested', 'TestNested_another']

    >>> @expand
    ... class Test(unittest.TestCase):
    ...     into_dict = {}
    ...
    ...     @expand(into=into_dict)
    ...     @foreach([123])
    ...     class TestNested(unittest.TestCase):
    ...         pass
    ...
    ...     @expand(into=into_dict)
    ...     @foreach([123])
    ...     class TestNested_another:  # (<- here we have an old-style class if Python 2.x is used)
    ...         pass
    ...
    >>> type(Test.TestNested) is Substitute
    True
    >>> type(Test.TestNested_another) is Substitute
    True
    >>> sorted(k for k in vars(Test).keys() if not k.startswith('_'))
    ['TestNested', 'TestNested_another', 'into_dict']
    >>> sorted(Test.into_dict.keys())
    ['TestNested__<123>', 'TestNested_another__<123>']

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

    >>> into_dict = {}
    >>> @expand(into=into_dict)
    ... @foreach([()])
    ... class Test(unittest.TestCase):
    ...
    ...     def setUp(self):
    ...         sys.stdout.write(
    ...             ' | .label={!r} | .context_targets={!r} | '.format(
    ...                 self.label,
    ...                 self.context_targets))
    ...         sys.stdout.flush()
    ...
    ...     def test(self):
    ...         self.assertEqual(self.label, '')
    ...         self.assertEqual(self.context_targets, [])
    ...
    >>> test_cls = into_dict.popitem()[1]
    >>> run_tests(test_cls)              # doctest: +ELLIPSIS
    test... | .label='' | .context_targets=[] | ok
    ...Ran 1 test...
    OK

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

__version__ = '0.4.4'


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
        context = _Context(context_manager_factory, *args, **kwargs)
        return self._clone_adding(context_list=[context])

    def label(self, text):
        return self._clone_adding(label_list=[text])

    @classmethod
    def _from_param_item(cls, param_item):
        if isinstance(param_item, param):
            return param_item
        if isinstance(param_item, tuple):
            return cls(*param_item)
        return cls(param_item)

    @classmethod
    def _combine_instances(cls, param_instances):
        new = cls()
        for param_inst in param_instances:
            new = new._clone_adding(
                args=param_inst._args,
                kwargs=param_inst._kwargs,
                context_list=param_inst._context_list,
                # (note: calling _get_label() here!)
                label_list=[param_inst._get_label()])
        return new

    def _clone_adding(self, args=None, kwargs=None,
                      context_list=None, label_list=None):
        new = self.__class__(*self._args, **self._kwargs)
        new._context_list.extend(self._context_list)
        new._label_list.extend(self._label_list)
        if args:
            new._args += tuple(args)
        if kwargs:
            conflicting = frozenset(new._kwargs).intersection(kwargs)
            if conflicting:
                raise ValueError(
                    'conflicting keyword arguments: ' +
                    ', '.join(sorted(map(repr, conflicting))))
            new._kwargs.update(kwargs)
        if context_list:
            new._context_list.extend(context_list)
        if label_list:
            new._label_list.extend(label_list)
        return new

    def _get_context_manager_factory(self):
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
                'def cm_factory():\n'
                '    context_targets = [None] * len(context_list)\n'
                '    {enclosing_withs}yield context_targets\n'.format(
                    # (note: if self._context_list is empty,
                    # enclosing_withs will be an empty string)
                    enclosing_withs=''.join(
                        ('with context_list[{0}]._make_context_manager() '
                         'as context_targets[{0}]:\n{next_indent}'
                        ).format(i, next_indent=((8 + 4 * i) * ' '))
                        for i in range(len(self._context_list)))))
            # Py2+Py3-compatible substitute of exec in a given namespace
            code = compile(src_code, '<string>', 'exec')
            namespace = {'context_list': self._context_list}
            eval(code, namespace)
            self.__cached_cm_factory = namespace['cm_factory']
            return self.__cached_cm_factory

    def _get_label(self):
        if self._label_list:
            return ', '.join(self._label_list)
        else:
            short_repr = self._short_repr
            args_reprs = (short_repr(val) for val in self._args)
            kwargs_reprs = ('{}={}'.format(key, short_repr(val))
                            for key, val in sorted(self._kwargs.items()))
            return ','.join(itertools.chain(args_reprs, kwargs_reprs))

    @staticmethod
    def _short_repr(obj, max_len=16):
        r = repr(obj)
        if len(r) > max_len:
            r = '<{}...>'.format(r.lstrip('<')[:max_len-5])
        return r


class paramseq(object):

    def __init__(*self_and_args, **kwargs):
        self = self_and_args[0]
        args = self_and_args[1:]
        self._init_with_appropriate_warn_stacklevel(args, kwargs)

    def _init_with_appropriate_warn_stacklevel(self, args, kwargs):
        if len(args) == 1 and not kwargs:
            # the sole positional argument is a parameter collection
            # (being a collection of: parameter values, tuples of such
            # values, or `param` instances)
            obj = self._warn_and_coerce_if_deprecated_type(args[0], warn_stacklevel=4)
            self._init_with_param_collections(obj)
        else:
            # each argument is a parameter value, or a tuple of such
            # values, or a `param` instance -- explicitly labeled if
            # the given argument is a keyword one
            self._init_with_param_collections(args, kwargs)

    def __add__(self, other):
        if self._is_legal_param_collection(other):
            other = self._warn_and_coerce_if_deprecated_type(other, warn_stacklevel=3)
            return self._from_param_collections(self, other)
        return NotImplemented

    def __radd__(self, other):
        if self._is_legal_param_collection(other):
            other = self._warn_and_coerce_if_deprecated_type(other, warn_stacklevel=3)
            return self._from_param_collections(other, self)
        return NotImplemented

    def _warn_and_coerce_if_deprecated_type(self, obj, warn_stacklevel):
        if isinstance(obj, tuple):
            warnings.warn(
                'using a tuple as a parameter collection will become '
                'illegal in the version 0.5.0 of unittest_expander.',
                DeprecationWarning,
                stacklevel=warn_stacklevel)
            obj = list(obj)  # (to avoid future redundant warn() calls)
        if _PY3 and isinstance(obj, (bytes, bytearray)):
            warnings.warn(
                'using a bytes or bytearray object as a parameter '
                'collection will become illegal in the version 0.5.0 '
                'of unittest_expander.',
                DeprecationWarning,
                stacklevel=warn_stacklevel)
            obj = list(obj)  # (to avoid future redundant warn() calls)
        return obj

    def context(self, context_manager_factory, *args, **kwargs):
        context = _Context(context_manager_factory, *args, **kwargs)
        new = self._from_param_collections(self)
        new._context_list.append(context)
        return new

    @classmethod
    def _from_param_collections(cls, *param_collections):
        self = cls.__new__(cls)
        self._init_with_param_collections(*param_collections)
        return self

    def _init_with_param_collections(self, *param_collections):
        for param_col in param_collections:
            if not self._is_legal_param_collection(param_col):
                raise TypeError(
                    '{!r} is not a legal parameter '
                    'collection'.format(param_col))
        self._param_collections = param_collections
        self._context_list = []

    @staticmethod
    def _is_legal_param_collection(obj):
        return (
            isinstance(obj, (
                paramseq,
                collections_abc.Sequence,
                collections_abc.Set,
                collections_abc.Mapping)
            ) and
            not isinstance(obj, _TEXT_STRING_TYPES)
        ) or callable(obj)

    def _generate_params(self, test_cls):
        for param_inst in self._generate_raw_params(test_cls):
            if self._context_list:
                param_inst = param_inst._clone_adding(
                    context_list=self._context_list)
            yield param_inst

    def _generate_raw_params(self, test_cls):
        for param_col in self._param_collections:
            if isinstance(param_col, paramseq):
                for param_inst in param_col._generate_params(test_cls):
                    yield param_inst
            elif isinstance(param_col, collections_abc.Mapping):
                for label, param_item in param_col.items():
                    yield param._from_param_item(param_item).label(label)
            else:
                if callable(param_col):
                    param_col = self._param_collection_callable_to_iterable(
                        param_col,
                        test_cls)
                else:
                    assert isinstance(param_col, (collections_abc.Sequence,
                                                  collections_abc.Set))
                for param_item in param_col:
                    yield param._from_param_item(param_item)

    @staticmethod
    def _param_collection_callable_to_iterable(param_col, test_cls):
        try:
            return param_col(test_cls)
        except TypeError:
            return param_col()


# test *method* or *class* decorator...
def foreach(*args, **kwargs):
    ps = paramseq.__new__(paramseq)
    ps._init_with_appropriate_warn_stacklevel(args, kwargs)
    def decorator(func_or_cls):
        stored_paramseq_objs = getattr(func_or_cls, _PARAMSEQ_OBJS_ATTR, None)
        if stored_paramseq_objs is None:
            stored_paramseq_objs = []
            setattr(func_or_cls, _PARAMSEQ_OBJS_ATTR, stored_paramseq_objs)
        assert isinstance(stored_paramseq_objs, list)
        stored_paramseq_objs.append(ps)
        if isinstance(func_or_cls, _CLASS_TYPES):
            warnings.warn(
                'decorating test *classes* with @foreach() will not be '
                'supported in the version 0.5.0 of unittest_expander.',
                DeprecationWarning,
                stacklevel=2)
        return func_or_cls
    return decorator


# test *class* decorator...
def expand(test_cls=None, **kwargs):
    if 'into' in kwargs:
        warnings.warn(
            'passing the `into` keyword argument to @expand() will '
            'become illegal in the version 0.5.0 of unittest_expander.',
            DeprecationWarning,
            stacklevel=2)
        into = kwargs.pop('into')
    else:
        into = kwargs.pop('__into_with_warning_already_emitted_if_needed', None)
    if kwargs:
        raise TypeError(
            'expand() got unexpected keyword arguments: ' +
            ', '.join(sorted(map(repr, kwargs))))
    if test_cls is None:
        return functools.partial(
            expand,
            __into_with_warning_already_emitted_if_needed=into)
    _expand_test_methods(test_cls)
    return _expand_test_cls(test_cls, into)

expand.global_name_pattern = None
expand.global_name_formatter = None


def _expand_test_methods(test_cls):
    attrs_to_substitute, attrs_to_add = _get_attrs_to_substitute_and_add(test_cls)
    for name, obj in attrs_to_substitute.items():
        setattr(test_cls, name, Substitute(obj))
    for name, obj in attrs_to_add.items():
        setattr(test_cls, name, obj)

def _get_attrs_to_substitute_and_add(test_cls):
    attr_names = dir(test_cls)
    seen_names = set(attr_names)
    attrs_to_substitute = dict()
    attrs_to_add = dict()
    for base_name in attr_names:
        obj = getattr(test_cls, base_name, None)
        base_func = _get_base_func(obj)
        if base_func is not None:
            paramseq_objs = _get_paramseq_objs(base_func)
            accepted_generic_kwargs = _get_accepted_generic_kwargs(base_func)
            for func in _generate_parametrized_functions(
                    test_cls, paramseq_objs,
                    base_name, base_func, seen_names,
                    accepted_generic_kwargs):
                attrs_to_add[func.__name__] = func
            attrs_to_substitute[base_name] = obj
    return attrs_to_substitute, attrs_to_add

def _get_base_func(obj):
    if (getattr(obj, _PARAMSEQ_OBJS_ATTR, None) is None
          or isinstance(obj, (Substitute, _CLASS_TYPES))):
        base_func = None
    else:
        base_func = _obtain_base_func_from(obj)
        assert inspect.isfunction(base_func)
    return base_func

def _get_paramseq_objs(base_func):
    paramseq_objs = getattr(base_func, _PARAMSEQ_OBJS_ATTR)
    assert isinstance(paramseq_objs, list)
    return paramseq_objs

def _get_accepted_generic_kwargs(base_func):
    accepted_generic_kwargs = _obtain_accepted_generic_kwargs_from(base_func)
    assert isinstance(accepted_generic_kwargs, set)
    return accepted_generic_kwargs

if _PY3:
    def _obtain_base_func_from(obj):
        # no unbound methods in Python 3
        if not isinstance(obj, types.FunctionType):
            raise TypeError('{!r} is not a function'.format(obj))
        return obj

    def _obtain_accepted_generic_kwargs_from(base_func):
        spec = inspect.getfullargspec(base_func)
        accepted_generic_kwargs = set(
            _GENERIC_KWARGS if spec.varkw is not None
            else (kw for kw in _GENERIC_KWARGS
                  if kw in (spec.args + spec.kwonlyargs)))
        return accepted_generic_kwargs
else:
    def _obtain_base_func_from(obj):
        if not isinstance(obj, types.MethodType):
            raise TypeError('{!r} is not a method'.format(obj))
        return obj.__func__

    def _obtain_accepted_generic_kwargs_from(base_func):
        spec = inspect.getargspec(base_func)
        accepted_generic_kwargs = set(
            _GENERIC_KWARGS if spec.keywords is not None
            else (kw for kw in _GENERIC_KWARGS
                  if kw in spec.args))
        return accepted_generic_kwargs


def _expand_test_cls(base_test_cls, into):
    paramseq_objs = getattr(base_test_cls, _PARAMSEQ_OBJS_ATTR, None)
    if paramseq_objs is None:
        return base_test_cls
    else:
        assert isinstance(paramseq_objs, list)
        if not isinstance(base_test_cls, _CLASS_TYPES):
            raise TypeError('{!r} is not a class'.format(base_test_cls))
        into = _resolve_the_into_arg(into, globals_frame_depth=3)
        seen_names = set(list(into.keys()) + [base_test_cls.__name__])
        for cls in _generate_parametrized_classes(
                base_test_cls, paramseq_objs, seen_names):
            into[cls.__name__] = cls
        return Substitute(base_test_cls)

def _resolve_the_into_arg(into, globals_frame_depth):
    orig_into = into
    if into is None:
        into = sys._getframe(globals_frame_depth).f_globals['__name__']
    if isinstance(into, _TEXT_STRING_TYPES):
        into = __import__(into, globals(), locals(), ['*'], 0)
    if inspect.ismodule(into):
        into = vars(into)
    if not isinstance(into, collections_abc.MutableMapping):
        raise TypeError(
            "resolved 'into' argument is not a mutable mapping "
            "({!r} given, resolved to {!r})".format(orig_into, into))
    return into


def _generate_parametrized_functions(test_cls, paramseq_objs,
                                     base_name, base_func, seen_names,
                                     accepted_generic_kwargs):
    for count, param_inst in enumerate(
            _generate_params_from_sources(paramseq_objs, test_cls),
            start=1):
        yield _make_parametrized_func(base_name, base_func, count, param_inst,
                                      seen_names, accepted_generic_kwargs)


def _generate_parametrized_classes(base_test_cls, paramseq_objs, seen_names):
    for count, param_inst in enumerate(
            _generate_params_from_sources(paramseq_objs, base_test_cls),
            start=1):
        yield _make_parametrized_cls(base_test_cls, count,
                                     param_inst, seen_names)


def _generate_params_from_sources(paramseq_objs, test_cls):
    src_params_iterables = [
        ps._generate_params(test_cls)
        for ps in paramseq_objs]
    for params_row in itertools.product(*src_params_iterables):
        yield param._combine_instances(params_row)


def _make_parametrized_func(base_name, base_func, count, param_inst,
                            seen_names, accepted_generic_kwargs):
    p_args = param_inst._args
    p_kwargs = param_inst._kwargs
    label = param_inst._get_label()
    cm_factory = param_inst._get_context_manager_factory()

    @functools.wraps(base_func)
    def generated_func(*args, **kwargs):
        args += p_args
        kwargs.update(**p_kwargs)
        with cm_factory() as context_targets:
            if 'context_targets' in accepted_generic_kwargs:
                kwargs.setdefault('context_targets', context_targets)
            if 'label' in accepted_generic_kwargs:
                kwargs.setdefault('label', label)
            return base_func(*args, **kwargs)

    delattr(generated_func, _PARAMSEQ_OBJS_ATTR)
    generated_func.__name__ = _format_name_for_parametrized(
        base_name, base_func, label, count, seen_names)
    _set_qualname(base_func, generated_func)
    return generated_func


def _make_parametrized_cls(base_test_cls, count, param_inst, seen_names):
    cm_factory = param_inst._get_context_manager_factory()
    label = param_inst._get_label()

    class generated_test_cls(base_test_cls):

        def setUp(self):
            self.label = label
            self.params = param_inst._args
            for name, obj in param_inst._kwargs.items():
                setattr(self, name, obj)
            ready_exit = None
            try:
                cm = cm_factory()
                enter, exit = _get_context_manager_enter_and_exit(cm)
                self.context_targets = enter()
                ready_exit = exit  # (note: from now on, exit can be called)
                self.__exit = exit
                try:
                    super_setUp = super(generated_test_cls, self).setUp
                except AttributeError:
                    r = None
                else:
                    r = super_setUp()
                return r
            except:
                suppress_exc = False
                if ready_exit is not None:
                    try:
                        suppress_exc = ready_exit(*sys.exc_info())
                    finally:
                        self.__exit = None
                if not suppress_exc:
                    raise

        def tearDown(self):
            try:
                try:
                    super_tearDown = super(generated_test_cls, self).tearDown
                except AttributeError:
                    r = None
                else:
                    r = super_tearDown()
            except:
                suppress_exc = False
                exit = self.__exit
                if exit is not None:
                    suppress_exc = exit(*sys.exc_info())
                if not suppress_exc:
                    raise
            else:
                exit = self.__exit
                if exit is not None:
                    exit(None, None, None)
                return r
            finally:
                self.__exit = None

    generated_test_cls.__module__ = base_test_cls.__module__
    generated_test_cls.__name__ = _format_name_for_parametrized(
        base_test_cls.__name__, base_test_cls, label, count, seen_names)
    _set_qualname(base_test_cls, generated_test_cls)
    return generated_test_cls


def _format_name_for_parametrized(base_name, base_obj,
                                  label, count, seen_names):
    pattern, formatter = _get_name_pattern_and_formatter()
    name = stem_name = formatter.format(
        pattern,
        base_name=base_name,
        base_obj=base_obj,
        label=label,
        count=count)
    uniq_tag = 2
    while name in seen_names:
        # ensure that, for a particular class, names are unique
        name = '{}__{}'.format(stem_name, uniq_tag)
        uniq_tag += 1
    seen_names.add(name)
    return name

def _get_name_pattern_and_formatter():
    pattern = getattr(expand, 'global_name_pattern', None)
    if pattern is None:
        pattern = _DEFAULT_PARAMETRIZED_NAME_PATTERN
    formatter = getattr(expand, 'global_name_formatter', None)
    if formatter is None:
        formatter = _DEFAULT_PARAMETRIZED_NAME_FORMATTER
    return pattern, formatter


def _set_qualname(base_obj, target_obj):
    # relevant to Python 3
    base_qualname = getattr(base_obj, '__qualname__', None)
    if base_qualname is not None:
        base_name = base_obj.__name__
        qualname_prefix = (
            base_qualname[:(len(base_qualname) - len(base_name))]
            if (base_qualname == base_name or
                base_qualname.endswith('.' + base_name))
            else '<...>.')
        target_obj.__qualname__ = qualname_prefix + target_obj.__name__
