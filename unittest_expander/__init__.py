# Copyright (c) 2014 Jan Kaliszewski (zuo). All rights reserved.
# Licensed under MIT License (see the LICENSE.txt file for details).

"""
*unittest_expander* is a Python library that provides flexible and
easy-to-use tools to parameterize your unit tests, especially those
based on :class:`unittest.TestCase` from the Python standard library.

The :mod:`unittest_expander` module provides the following tools:

* test case class decorator: :func:`expand`,
* test case method (or class) decorator: :func:`foreach`,
* two helper classes: :class:`param` and :class:`paramseq`.

Let's see how to use them...


.. _expand-and-foreach-basics:

Basic use of :func:`expand` and :func:`foreach`
===============================================

Assume we have a (somewhat trivial, in fact) function that checks
whether the given number is even or not:

>>> def is_even(n):
...     return n % 2 == 0

Of course, in the real world the code we write is usually more
interesting...  Anyway, most often we want to test how does it work for
different parameters.  And usually it is not the best idea to test many
cases in a loop within one test method -- because of lack of test
isolation, less information on failures, harder debugging etc.  So let's
write our tests in a smarter way:

>>> import unittest
>>> from unittest_expander import expand, foreach
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach([0, 2, -14])
...     def test_even(self, n):
...         self.assertTrue(is_even(n))
...
...     @foreach([-1, 17])
...     def test_odd(self, n):
...         self.assertFalse(is_even(n))

As you see, it's fairly simple: you attach parameter collections to your
test methods with the :func:`foreach` decorator and decorate the whole
test case class with the :func:`expand` decorator.  The latter does the
actual job, i.e. generates (and adds to the test case class)
parameterized versions of the methods.

Let's run this stuff...

>>> # a helper function to run tests in our examples
>>> # -- of course, normally YOU DON'T NEED IT
>>> import sys
>>> def run_tests(*test_case_classes):
...     suite = unittest.TestSuite(
...         unittest.TestLoader().loadTestsFromTestCase(cls)
...         for cls in test_case_classes)
...     unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
...
>>> # adding it just to demonstrate that particular tests are really isolated
>>> Test_is_even.setUp = lambda s: sys.stdout.write(' *** new test setUp *** ')
>>> 
>>> # get on with it! (oh, anyway, on to scene twenty-four...)
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even__<-14> ... *** new test setUp *** ok
test_even__<0> ... *** new test setUp *** ok
test_even__<2> ... *** new test setUp *** ok
test_odd__<-1> ... *** new test setUp *** ok
test_odd__<17> ... *** new test setUp *** ok
...Ran 5 tests...
OK

To test our *is_even()* function we created two test case methods --
each accepting one parameter value.

Another approach could be to define one method that accepts a couple of
arguments:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach([
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

Parameters can also be specified in a more descriptive way -- with
keyword arguments.  It is possible when you use :class:`param` objects
instead of tuples:

>>> from unittest_expander import param
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach([
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
...     @foreach([
...         param(sys.maxsize, expected=False).label('sys.maxsize'),
...         param(-sys.maxsize, expected=False).label('-sys.maxsize'),
...     ])
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

*If* a test method accepts the `label` keyword argument, the appropriate
label (either auto-generated from parameter values or explicitly
specified, e.g. with :meth:`param.label`) will be passed in as that
argument:

>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     @foreach([
...         param(sys.maxsize, expected=False).label('sys.maxsize'),
...         param(-sys.maxsize, expected=False).label('-sys.maxsize'),
...     ])
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

Other ways to label your tests explicitly
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

Just transform them (or at least the first one) into :class:`paramseq`
instances -- and then add one to another:

>>> from unittest_expander import paramseq
>>> 
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     basic_params = paramseq([
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True).label('just zero, because why not?'),
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
...         # using keyword arguments: the same as passing a dict
...         noninteger=param(1.2345, expected=False),
...         horribleabuse=param('%s', expected=False),
...     )
...
...     spam = {
...         '18->True': (18, True),
...     }
...
...     ham = [
...         param(12399999999999999, False),
...         param(n=12399999999999998, expected=True),
...     ]
...
...     # just add them one to another (producing a new paramseq)
...     all_params = basic_params + huge_params + strange_params + spam + ham
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
test_is_even__<-sys.maxsize> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<18->True> ... ok
test_is_even__<2,expected=True> ... ok
test_is_even__<<12399999999...>,False> ... ok
test_is_even__<expected=True,n=<12399999999...>> ... ok
test_is_even__<horribleabuse> ... ok
test_is_even__<just zero, because why not?> ... ok
test_is_even__<noninteger> ... ok
test_is_even__<sys.maxsize> ... ok
...Ran 12 tests...
OK

Note that the parameter collections
(sequences/mappings/sets/:class:`paramseq` instances) do not need to be
created or bound within the test case class body; you could, for
example, import them from a separate module.  Obviously, it makes code
reuse and refactorization easier.

A :class:`paramseq` instance can also be created from a callable object
that returns a sequence or another iterable (e.g. a generator).

>>> from random import randint
>>> 
>>> @paramseq   # <- yes, used as a decorator
... def randomized(test_case_cls):
...     yield param(randint(test_case_cls.FROM, test_case_cls.TO) * 2,
...                 expected=True).label('random even')
...     yield param(randint(test_case_cls.FROM, test_case_cls.TO) * 2 + 1,
...                 expected=False).label('random odd')
...
>>> @expand
... class Test_is_even(unittest.TestCase):
...
...     FROM = -(10 ** 6)
...     TO = 10 ** 6
...
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
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<-1,expected=False> ... ok
test_is_even__<-14,expected=True> ... ok
test_is_even__<0,expected=True> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<2,expected=True> ... ok
test_is_even__<random even> ... ok
test_is_even__<random odd> ... ok
...Ran 7 tests...
OK

Note: the callable object that was passed into the :class:`paramseq`
constructor (in this case a generator function) is called (and its
iterable result is iterated over) when the :func:`expand` decorator
is being executed, *before* generating parameterized test methods.

The callable object can accept no arguments or one positional argument
-- in the latter case the test case class is passed in.


.. _foreach-cartesian:

Combining several :func:`foreach` to get Cartesian product
==========================================================

You can apply two or more :func:`foreach` decorators to the same test
method -- to combine several parameter collections to obtain Cartesian
product of them:

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
...     input_values_and_results = randomized + [
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
...         float=float,
...     )
...
...     # let's combine them (7 * 2 -> 14 parameterized tests)
...     @foreach(input_values_and_results)
...     @foreach(input_types)
...     def test_is_even(self, input_type, n, expected):
...         n = input_type(n)
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<float, -1,expected=False> ... ok
test_is_even__<float, -14,expected=True> ... ok
test_is_even__<float, 0,expected=True> ... ok
test_is_even__<float, 17,expected=False> ... ok
test_is_even__<float, 2,expected=True> ... ok
test_is_even__<float, random even> ... ok
test_is_even__<float, random odd> ... ok
test_is_even__<integer, -1,expected=False> ... ok
test_is_even__<integer, -14,expected=True> ... ok
test_is_even__<integer, 0,expected=True> ... ok
test_is_even__<integer, 17,expected=False> ... ok
test_is_even__<integer, 2,expected=True> ... ok
test_is_even__<integer, random even> ... ok
test_is_even__<integer, random odd> ... ok
...Ran 14 tests...
OK


.. _context-basics:

Fixtures -- part I: :meth:`param.context`
=========================================

When dealing with resources managed with `context managers`_, you can
specify a *context manager factory* and its arguments using the
:meth:`~param.context` method of a :class:`param` object -- then each
call of the resultant parameterized test will be enclosed in a dedicated
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
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<load='',save=''> ... ok
test_save_load__<load='abc',save='abc'> ... ok
...Ran 2 tests...
OK

Note: *if* a test method accepts the `context_targets` keyword argument,
a list of context manager *as-targets* (i.e. objects returned by context
managers' :meth:`__enter__`) will be passed in as that argument.

It is a list because there can be more than one *context* per parameter
collection's item, e.g.:

>>> import contextlib
>>> @contextlib.contextmanager
... def memo_cm(tag):
...     memo.append('enter:' + tag)
...     yield tag
...     memo.append('exit:' + tag)
...
>>> memo = []
>>> 
>>> @expand
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = [
...         (
...             param(save='', load='', expected_tag='FOO')
...               .context(NamedTemporaryFile, 'w+t')  # (outer one)
...               .context(memo_cm, tag='FOO')         # (inner one)
...         ),
...         (
...             param(save='abc', load='abc', expected_tag='BAR')
...               .context(NamedTemporaryFile, 'w+t')
...               .context(memo_cm, tag='BAR')
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
...         memo.append('test')
...
>>> memo == []
True
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<expected_tag='BAR',load='abc',save='abc'> ... ok
test_save_load__<expected_tag='FOO',load='',save=''> ... ok
...Ran 2 tests...
OK
>>> memo == [
...     'enter:BAR', 'test', 'exit:BAR',
...     'enter:FOO', 'test', 'exit:FOO',
... ]
True

Contexts are properly dispatched (context managers' :meth:`__enter__`
and :meth:`__exit__` are properly called...) -- also when errors occur:

>>> @contextlib.contextmanager
... def err_memo_cm(tag):
...     memo.append('enter:' + tag)
...     try:
...         if tag.endswith('context-enter-error'):
...             raise RuntimeError('error in __enter__')
...         else:
...             yield tag
...             if tag.endswith('context-exit-error'):
...                 raise RuntimeError('error in __exit__')
...     except:
...         memo.append('ERR-exit:' + tag)
...         raise
...     else:
...         memo.append('exit:' + tag)
...
>>> memo = []
>>> err_params = [
...     (
...         param().label('no_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner')
...     ),
...     (
...         param().label('test_fail')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner')
...     ),
...     (
...         param().label('test_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner')
...     ),
...     (
...         param().label('inner_context_enter_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner-context-enter-error')
...     ),
...     (
...         param().label('inner_context_exit_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner-context-exit-error')
...     ),
...     (
...         param().label('outer_context_enter_error')
...                .context(err_memo_cm, tag='outer-context-enter-error')
...                .context(err_memo_cm, tag='inner')
...     ),
...     (
...         param().label('outer_context_exit_error')
...                .context(err_memo_cm, tag='outer-context-exit-error')
...                .context(err_memo_cm, tag='inner')
...     ),
... ]
>>> 
>>> @expand
... class SillyTest(unittest.TestCase):
...
...     def setUp(self):
...         memo.append('setUp')
...
...     def tearDown(self):
...         memo.append('tearDown')
...
...     @foreach(err_params)
...     def test(self, label):
...         if label == 'test_fail':
...             memo.append('FAIL-test')
...             self.fail()
...         elif label == 'test_error':
...             memo.append('ERROR-test')
...             raise RuntimeError
...         else:
...             memo.append('test')
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
>>> memo == [
...     # inner_context_enter_error
...     'setUp',
...     'enter:outer',
...     'enter:inner-context-enter-error',
...     'ERR-exit:inner-context-enter-error',
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
...     'enter:outer-context-enter-error',
...     'ERR-exit:outer-context-enter-error',
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

Note: contexts attached to test *method* params (in contrast to those
attached to test *class* params -- see below:
:ref:`foreach-as-class-decorator`) are dispatched *directly* before
(:meth:`__enter__`) and after (:meth:`__exit__`) a given parameterized
test method call, that is, *after* :meth:`setUp` and *before*
:meth:`tearDown` calls -- so :meth:`setUp` and :meth:`tearDown` are
unaffected by any errors related to those contexts.

On the other hand, an error in :meth:`setUp` prevents a test from being
called -- then contexts are not dispatched at all:

>>> def setUp(self):
...     memo.append('setUp')
...     raise ValueError
...
>>> SillyTest.setUp = setUp
>>> memo = []
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
>>> memo == ['setUp', 'setUp', 'setUp', 'setUp', 'setUp', 'setUp', 'setUp']
True


.. _paramseq-context:

Convenience shortcut: :meth:`paramseq.context`
==============================================

You can use the method :meth:`paramseq.context` to apply the given
context properties to *all* parameter items the :class:`paramseq`
instance aggregates:

>>> @expand
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = paramseq([
...         param(save='', load=''),
...         param(save='abc', load='abc'),
...     ]).context(NamedTemporaryFile, 'w+t')
...
...     @foreach(params_with_contexts)
...     def test_save_load(self, save, load, context_targets):
...         file = context_targets[0]
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

Note: :meth:`paramseq.context` as well as :meth:`param.context` and
:meth:`param.label` methods create new objects (respectively
:class:`paramseq` or :class:`param` instances), without modifying
the existing ones.

>>> pseq1 = paramseq([1, 2, 3])
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

Fixtures -- part II: :func:`foreach` as a class decorator
=========================================================

:func:`foreach` can be used not only as a test case *method* decorator
but also as a test case *class* decorator -- to generate parameterized
test case *classes*.

That allows you to share each specified parameter/context/label across
all test methods.  Parameters (and labels, and context targets) are
accessible as instance attributes (*not* as method arguments) from any
test method, as well as from the :meth:`setUp` and :meth:`tearDown`
methods.

>>> params_with_contexts = paramseq([                         # 2 param items
...     param(save='', load=''),
...     param(save='abc', load='abc'),
... ]).context(NamedTemporaryFile, 'w+t')
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
...         # (note: on Python 2.7+ we could resign from using contexts
...         # and just use unittest.TestCase.addCleanup() here...)
...
...     @foreach([param(suffix=' '), param(suffix='XX')])     # 2 param items
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
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
>>> # (note: 2 * 2 * 2 param items -> 8 parameterized tests)
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__<suffix=' '> (..._<'foo',b=42, load='',save=''>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='',save=''>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='',save=''>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='',save=''>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='abc',save='abc'>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='abc',save='abc'>) ... ok
...Ran 8 tests...
OK

As you see, you can combine :func:`foreach` as *class* decorator(s) with
:func:`foreach` as *method* decorator(s) -- you will obtain tests
parameterized with the Cartesian product of the involved parameter
collections.

Note: when using :func:`foreach` as a *class* decorator you must
remember to place :func:`expand` as the topmost (the outer) class
decorator (above all :func:`foreach` decorators).

The *into* keyword argument for the :func:`expand` decorator specifies
where the generated (parameterized) subclasses of the decorated test
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
test_save_load (...TestSaveLoad__<load='',save=''>) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>) ... ok
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
test_save_load (...TestSaveLoad__<load='',save=''>) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>) ... ok
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
test_save_load (...TestSaveLoadIt__<load='',save=''>) ... ok
test_save_load (...TestSaveLoadIt__<load='abc',save='abc'>) ... ok
...Ran 2 tests...
OK

Contexts are, obviously, properly dispatched -- also when errors occur:

>>> memo = []              # see earlier definition of err_memo_cm()...
>>> err_params.extend([    # see earlier initialization of err_params...
...     (
...         param().label('setUp_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner')
...     ),
...     (
...         param().label('tearDown_error')
...                .context(err_memo_cm, tag='outer')
...                .context(err_memo_cm, tag='inner')
...     ),
... ])
>>> into_dict = {}  # this time we'll pass another mapping than globals()...
>>> 
>>> @expand(into=into_dict)
... @foreach(err_params)
... class SillyTest(unittest.TestCase):
...
...     def setUp(self):
...         if self.label == 'setUp_error':
...             memo.append('ERR-setUp')
...             raise RuntimeError
...         memo.append('setUp')
...
...     def tearDown(self):
...         if self.label == 'tearDown_error':
...             memo.append('ERR-tearDown')
...             raise RuntimeError
...         memo.append('tearDown')
...
...     def test(self):
...         if self.label == 'test_fail':
...             memo.append('FAIL-test')
...             self.fail()
...         elif self.label == 'test_error':
...             memo.append('ERROR-test')
...             raise RuntimeError
...         else:
...             memo.append('test')
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
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
test (...SillyTest__<inner_context_enter_error>) ... ERROR
test (...SillyTest__<inner_context_exit_error>) ... ERROR
test (...SillyTest__<no_error>) ... ok
test (...SillyTest__<outer_context_enter_error>) ... ERROR
test (...SillyTest__<outer_context_exit_error>) ... ERROR
test (...SillyTest__<setUp_error>) ... ERROR
test (...SillyTest__<tearDown_error>) ... ERROR
test (...SillyTest__<test_error>) ... ERROR
test (...SillyTest__<test_fail>) ... FAIL
...Ran 9 tests...
FAILED (failures=1, errors=7)
>>> memo == [
...     # inner_context_enter_error
...     'enter:outer',
...     'enter:inner-context-enter-error',
...     'ERR-exit:inner-context-enter-error',
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
...     'enter:outer-context-enter-error',
...     'ERR-exit:outer-context-enter-error',
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

Note: contexts attached to test *class* params (in contrast to those
attached to test *method* params -- see: :ref:`context-basics`) are
automatically dispatched within :meth:`setUp` and (if applicable)
:meth:`tearDown` -- so :meth:`setUp` and :meth:`tearDown` *are* affected
by errors related to those contexts.  On the other hand, context
finalization is *not* affected by any exceptions from actual test
methods (i.e.  context managers' :meth:`__exit__` methods are always
called with ``None, None, None`` arguments unless :meth:`tearDown` or an
enclosed context manager's :meth:`__exit__` raises an exception).


.. _about-substitute:

:class:`Substitute` objects
===========================

One could ask: "What the :func:`expand` decorator does with the original
objects (classes or methods) decorated with :func:`foreach`?"

>>> @expand
... @foreach(useless_data)
... class DummyTest(unittest.TestCase):
...
...     @foreach([1, 2])
...     def test_it(self, x):
...         pass
...
...     attr = [42]
...     test_it.attr = [43, 44]

They cannot be left where they are because, without parameterization,
they are not valid tests (but rather kind of test templates).  For that
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
>>> (set(dir(DummyTest.actual_object)) - set(['__call__'])
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
>>> (set(dir(test_it.actual_object)) - set(['__call__'])
...  ).issubset(dir(test_it))
True

As you see, such a :class:`Substitute` instance is kind of a
non-callable proxy to the original class or method (preventing it from
being included by test loaders but still keeping it available, e.g. for
introspection).


.. _custom-name-formatting:

Custom method/class name formatting
===================================

If you don't like how parameterized method/class names are formatted --
you can customize that globally by:

* setting :attr:`expand.global_name_pattern` to a :meth:`str.format`-like
  formattable pattern containing zero or more of the following format
  fields:

  * ``{base_name}`` -- the name of the original test method or class,
  * ``{base_obj}`` -- the original test method or class,
  * ``{label}`` -- generated representation of parameter values or an
    explicitly specified label,
  * ``{count}`` -- consecutive number of a generated parameterized
    method or class;

  (in future versions of the library other format fields may be added)

and/or

* setting :attr:`expand.global_name_formatter` to an instance of a
  custom subclass of the :class:`string.Formatter` class from the
  Python standard library (or to any object whose :meth:`format`
  method acts similarily to :meth:`string.Formatter.format`).

For example:

>>> expand.global_name_pattern = '{base_name}__parameterized_{count}'
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
...     @foreach([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
'TestSaveLoad__parameterized_1'
'TestSaveLoad__parameterized_2'
'TestSaveLoad__parameterized_3'
'TestSaveLoad__parameterized_4'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__parameterized_1 (...TestSaveLoad__parameterized_1) ... ok
test_save_load__parameterized_2 (...TestSaveLoad__parameterized_1) ... ok
test_save_load__parameterized_1 (...TestSaveLoad__parameterized_2) ... ok
test_save_load__parameterized_2 (...TestSaveLoad__parameterized_2) ... ok
test_save_load__parameterized_1 (...TestSaveLoad__parameterized_3) ... ok
test_save_load__parameterized_2 (...TestSaveLoad__parameterized_3) ... ok
test_save_load__parameterized_1 (...TestSaveLoad__parameterized_4) ... ok
test_save_load__parameterized_2 (...TestSaveLoad__parameterized_4) ... ok
...Ran 8 tests...
OK

...or, let's say:

>>> import string
>>> class SillyFormatter(string.Formatter):
...     def format(self, format_string, *args, **kwargs):
...         label = kwargs['label']
...         if '42' in label:
...             return '!{0}!'.format(label)
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
... @foreach(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     @foreach([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
"!'foo',b=42, load='',save=''!"
"!'foo',b=42, load='abc',save='abc'!"
'TestSaveLoad^^parameterized^3'
'TestSaveLoad^^parameterized^4'
>>> 
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__parameterized_1 (...!'foo',b=42, load='',save=''!) ... ok
test_save_load__parameterized_2 (...!'foo',b=42, load='',save=''!) ... ok
test_save_load__parameterized_1 (...!'foo',b=42, load='abc',save='abc'!) ... ok
test_save_load__parameterized_2 (...!'foo',b=42, load='abc',save='abc'!) ... ok
test_save_load__parameterized_1 (...TestSaveLoad^^parameterized^3) ... ok
test_save_load__parameterized_2 (...TestSaveLoad^^parameterized^3) ... ok
test_save_load__parameterized_1 (...TestSaveLoad^^parameterized^4) ... ok
test_save_load__parameterized_2 (...TestSaveLoad^^parameterized^4) ... ok
...Ran 8 tests...
OK

Set those attributes to :obj:`None` to restore the default behaviour:

>>> expand.global_name_pattern = None
>>> expand.global_name_formatter = None


.. _avoiding-name-clashes:

Name clashes avoided automatically
==================================

:func:`expand` tries to avoid name clashes: when it detects a clash it
adds a suffix to a newly formatted name, e.g.:

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
...     @foreach([
...         0,
...         4,
...         0,   # <- repeated parameter value
...         0,   # <- repeated parameter value
...         -16,
...         0,   # <- repeated parameter value
...     ])
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
test_even__<-16> (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<0> (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<0>__2 (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<0>__3 (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<0>__4 (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<4>__3 (...Test_is_even__<'foo',b=42>__2) ... ok
test_even__<-16> (...Test_is_even__<'foo',b=433>) ... ok
test_even__<0> (...Test_is_even__<'foo',b=433>) ... ok
test_even__<0>__2 (...Test_is_even__<'foo',b=433>) ... ok
test_even__<0>__3 (...Test_is_even__<'foo',b=433>) ... ok
test_even__<0>__4 (...Test_is_even__<'foo',b=433>) ... ok
test_even__<4>__3 (...Test_is_even__<'foo',b=433>) ... ok
...Ran 12 tests...
OK

.. doctest::
    :hide:

    Some less typical usage cases
    =============================

    For completeness, let's also check some less typical usage cases and
    error conditions...

    >>> isinstance(paramseq(), paramseq)
    True
    >>> isinstance(paramseq(set([1, 2])), paramseq)
    True
    >>> isinstance(paramseq(a=3, b=4), paramseq)
    True
    >>> isinstance(paramseq(paramseq([1, 2])), paramseq)
    True
    >>> isinstance(paramseq([1, 2]) + set([3, 4]) + (5, 6), paramseq)
    True
    >>> isinstance(set([3, 4]) + paramseq([1, 2]) + (5, 6), paramseq)
    True

    >>> paramseq([1, 2], [3, 4])     # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...takes 1 or 2 positional arguments...

    >>> paramseq([1, 2], a=3, b=4)   # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...either one positional...or some keyword...not both...

    >>> paramseq([1, 2]) + 3         # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> 3 + paramseq([1, 2])         # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...

    >>> paramseq('123')              # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...not a legal parameter source class...

    >>> expand(illegal_arg='spam')   # doctest: +ELLIPSIS
    Traceback (most recent call last):
    TypeError: ...unexpected keyword arguments...

    >>> @expand(into=['badtype'])    # doctest: +ELLIPSIS
    ... @foreach([1, 2])
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

    >>> memo = []
    >>> @expand
    ... class Test(unittest.TestCase):
    ...     @foreach([
    ...         param(),
    ...     ])
    ...     def test(self, **kwargs):
    ...         # **kwargs means accepting `label` and `context_targets`
    ...         memo.append(sorted(kwargs.keys()))
    ...
    >>> run_tests(Test)              # doctest: +ELLIPSIS
    test__<> ... ok
    ...Ran 1 test...
    OK
    >>> memo == [
    ...     ['context_targets', 'label'],
    ... ]
    True
    >>> type(Test.test) is Substitute
    True

    >>> import sys
    >>> no_qn = sys.version_info < (3, 3)
    >>> no_qn or getattr(Test, 'test__<>').__qualname__ == 'Test.test__<>'
    True

    >>> into_dict = {}
    >>> @expand(into=into_dict)
    ... @foreach([42])
    ... class Test(unittest.TestCase):
    ...     pass
    ...
    >>> no_qn or into_dict['Test__<42>'].__qualname__ == 'Test__<42>'
    True

    >>> memo = []
    >>> @expand
    ... class Test(object):  # not a unittest.TestCase subclass
    ...     @foreach([1, 2, 3, 4])
    ...     def test(self, n):
    ...         memo.append(n)
    ...
    >>> t = Test()
    >>> type(t.test) is Substitute
    True
    >>> memo == []
    True
    >>> getattr(t, 'test__<1>')()
    >>> memo == [1]
    True
    >>> getattr(t, 'test__<2>')()
    >>> memo == [1, 2]
    True
    >>> getattr(t, 'test__<3>')()
    >>> memo == [1, 2, 3]
    True
    >>> getattr(t, 'test__<4>')()
    >>> memo == [1, 2, 3, 4]
    True
"""

from unittest_expander._internal import (
    foreach,
    expand,
    param,
    paramseq,
    Substitute,
)

__all__ = (
    'foreach',
    'expand',
    'param',
    'paramseq',
    'Substitute',
)


foreach.__module__ = __name__
expand.__module__ = __name__
param.__module__ = __name__
paramseq.__module__ = __name__
Substitute.__module__ = __name__
