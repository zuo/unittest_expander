"""
The library provides the following utilities:

* test case method (or class) decorator: @expand,
* test case class decorator: @parametrize,
* two helper classes: param and paramseq.

How to use them?

Let's assume we have a (somewhat trivial, in fact) function that checks
whether the given number is even or not:

>>> def is_even(n):
...     return n % 2 == 0

For such a trivial function it seems to be enough but in the real world
our code units and their tests are more complex, and usually it is a bad
idea to test many cases within one test case method (harder debugging,
lack of test separation...).

So let's prepare our tests in a smarter way:

>>> import unittest, sys
>>>
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
...         sys.stdout.write(' *** Note: separate instance and setUp *** ')
...
>>> def run_tests(*test_case_classes):
...     suite = unittest.TestSuite(
...         unittest.TestLoader().loadTestsFromTestCase(cls)
...         for cls in test_case_classes)
...     unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_even__<-14> ... *** Note: separate instance and setUp *** ok
test_even__<0> ... *** Note: separate instance and setUp *** ok
test_even__<2> ... *** Note: separate instance and setUp *** ok
test_odd__<-1> ... *** Note: separate instance and setUp *** ok
test_odd__<17> ... *** Note: separate instance and setUp *** ok
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
test_is_even__<-1,False> ... ok
test_is_even__<-14,True> ... ok
test_is_even__<0,True> ... ok
test_is_even__<17,False> ... ok
test_is_even__<2,True> ... ok
...
Ran 5 tests...
OK

It could also be written in more descriptive way, i.e. also using
keyword arguments (especially useful when there are more test method
parameters):

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
test_is_even__<-1,expected=False> ... ok
test_is_even__<-14,expected=True> ... ok
test_is_even__<0,expected=True> ... ok
test_is_even__<17,expected=False> ... ok
test_is_even__<2,expected=True> ... ok
...
Ran 5 tests...
OK

But what to do, if we need to *label* our parameters explicitly?
We can use a dict:

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
test_is_even__<-sys.maxsize> ... ok
test_is_even__<sys.maxsize> ... ok
...
Ran 2 tests...
OK

...or just the label() method of `param` objects:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     @expand([
...         param(1.2345, expected=False).label('noninteger'),
...         param('%s', expected=False).label('string'),
...     ])
...     def test_is_even(self, n, expected, label):
...         actual = is_even(n)
...         self.assertTrue(isinstance(actual, bool))
...         self.assertEqual(actual, expected)
...         assert label in ('noninteger', 'string')
...
>>> run_tests(Test_is_even)  # doctest: +ELLIPSIS
test_is_even__<noninteger> ... ok
test_is_even__<string> ... ok
...
Ran 2 tests...
OK

(Note: if a test method accepts the `label` keyword argument, the
appropriate label -- either explicitly specified or auto-generated --
will be passed in as that argument.)

But now, how to concatenate separately defined param collections?
(sequences, mappings or sets)

Let's transform them into `paramseq` instances and then just add one to
another:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     basic_params = paramseq([
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True).label('just zero, why not?'),
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
...         string=param('%s', expected=False),
...     )
...
...     spam = paramseq(set([
...         (18, True),
...     ]))
...
...     # just add them -- one to another
...     all_params = basic_params + huge_params + strange_params + spam
...
...     @expand(all_params)
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
test_is_even__<18,True> ... ok
test_is_even__<2,expected=True> ... ok
test_is_even__<just zero, why not?> ... ok
test_is_even__<noninteger> ... ok
test_is_even__<string> ... ok
test_is_even__<sys.maxsize> ... ok
...
Ran 10 tests...
OK

Note that the sequences/mappings/sets/paramseq instances do not need
to be created or bound within the class body -- you could e.g. import
them from a separate module.  Obviously, it makes code reuse and
refactorization easier.

A `paramseq` instance can also be created from a callable object that
returns a sequence or other iterable (e.g. generator).  Let's assume
we need to generate some random param values:

>>> from random import randint
>>> @paramseq
... def randomized(test_case_cls):
...     yield param(randint(test_case_cls.FROM, test_case_cls.TO) * 2,
...                 expected=True).label('random even')
...     yield param(randint(test_case_cls.FROM, test_case_cls.TO) * 2 + 1,
...                 expected=False).label('random odd')
...
>>> @parametrize
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
...     @expand(input_values_and_results)
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
...
Ran 7 tests...
OK

Note: the callable object (in this case a generator function) is called
-- and its iterable result iterated over -- when the @parametrize
decorator is called, before generating parametrized test methods.
The callable object can take zero arguments or one positional argument
-- in the latter case the test case class is passed in.

Another feature: combining different parameter sequences/sets/
/mappings/paramseq instances -- to produce cartesian product of
their elements -- just by applying two or more @expand decorators:

>>> @parametrize
... class Test_is_even(unittest.TestCase):
...
...     FROM = -(10 ** 6)
...     TO = 10 ** 6
...
...     # first param 'dimension' (7 param rows)
...     @paramseq
...     def randomized(cls):
...         yield param(randint(cls.FROM, cls.TO) * 2,
...                     expected=True).label('random even')
...         yield param(randint(cls.FROM, cls.TO) * 2 + 1,
...                     expected=False).label('random odd')
...     input_values_and_results = randomized + [
...         param(-14, expected=True),
...         param(-1, expected=False),
...         param(0, expected=True),
...         param(2, expected=True),
...         param(17, expected=False),
...     ]
...
...     # second param 'dimension' (2 param rows)
...     input_types = dict(
...         integer=int,
...         float=float,
...     )
...
...     # let's combine them (-> 14 param rows)
...     @expand(input_values_and_results)
...     @expand(input_types)
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
...
Ran 14 tests...
OK

And what about fixtures?  Sometimes the standard setUp()/tearDown()
(and addCleanup()) are just not enough (or not enough convenient).
Then you can use:

* either the context() method of `param` objects,
* or @expand as a test case *class* decorator.

Let's start with the former possibility.  You can specify a context
manager factory and its arguments, with the context() method of `param`
objects.  The context manager factory will be called (with the specified
arguments) to create a context manager before each test method call
(each call will be enclosed in a dedicated context manager instance).

>>> from tempfile import NamedTemporaryFile
>>> @parametrize
... class TestSaveLoad(unittest.TestCase):
...
...     data_with_contexts = [
...         param(save='', load='').context(NamedTemporaryFile, 'w+t'),
...         param(save='abc', load='abc').context(NamedTemporaryFile, 'w+t'),
...     ]
...
...     @expand(data_with_contexts)
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
...
Ran 2 tests...
OK

Note: if a test method takes the `context_targets` keyword argument,
a list of context manager `as` targets (i.e. objects bound with the
`with ... as` clause) will be passed in as that argument.

It is a list because there can be more than one context per param, e.g.:

>>> import contextlib
>>> @contextlib.contextmanager
... def memo_cm(tag):
...     memo.append('enter:' + tag)
...     yield tag
...     memo.append('exit:' + tag)
...
>>> memo = []
>>>
>>> @parametrize
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
...     @expand(params_with_contexts)
...     def test_save_load(self, save, load, expected_tag, context_targets):
...         file, tag = context_targets
...         assert tag == expected_tag
...         file.write(save)
...         file.seek(0)
...         load_actually = file.read()
...         self.assertEqual(load_actually, load)
...         memo.append('test')
...
>>> memo
[]
>>> run_tests(TestSaveLoad)  # doctest: +ELLIPSIS
test_save_load__<expected_tag='BAR',load='abc',save='abc'> ... ok
test_save_load__<expected_tag='FOO',load='',save=''> ... ok
...
Ran 2 tests...
OK
>>> memo == [
...     'enter:BAR', 'test', 'exit:BAR',
...     'enter:FOO', 'test', 'exit:FOO',
... ]
True

Contexts are properly dispatched (context managers' __enter__ and
__exit__ are properly called...) also when errors occur:

>>> @contextlib.contextmanager
... def err_memo_cm(tag):
...     memo.append('enter:' + tag)
...     try:
...         if tag.endswith('context-enter-error'):
...             raise RuntimeError
...         else:
...             yield tag
...             if tag.endswith('context-exit-error'):
...                 raise RuntimeError
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
>>> @parametrize
... class SillyTest(unittest.TestCase):
...
...     def setUp(self):
...         memo.append('setUp')
...
...     def tearDown(self):
...         memo.append('tearDown')
...
...     @expand(err_params)
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
...
Ran 7 tests...
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

(Note: contexts attached to test *method* params [in contrast to those
attached to test *class* params -- see below: applying @expand to test
case classes...] are dispatched *directly* before and after a given test
method (__enter__/__exit__), that is, *after* setUp() and *before*
tearDown() -- so setUp() and tearDown() are unaffected by any errors
related to those contexts.  On the other hand, an exception in setUp()
would cause that a given test method would not be called and contexts
would not be dispatched at all.)

If all context properties within a paramseq are the same you can,
as a shortcut, use the paramseq.context() method -- to apply the
given context properties to all params:

>>> @parametrize
... class TestSaveLoad(unittest.TestCase):
...
...     params_with_contexts = paramseq([
...         param(save='', load=''),
...         param(save='abc', load='abc'),
...     ]).context(NamedTemporaryFile, 'w+t')
...
...     @expand(params_with_contexts)
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
...
Ran 2 tests...
OK

Note: paramseq.context() as well as param.context() and param.label()
create new objects, without modifying the existing ones.  Generally,
these types (param and paramseq) should be considered immutable.

>>> pseq = paramseq([1, 2, 3])
>>> pseq2 = pseq.context(open, '/etc/hostname', 'rb')
>>> pseq is not pseq2
True
>>> isinstance(pseq, paramseq) and isinstance(pseq2, paramseq)
True

>>> p = param(1, 2, c=3)
>>> p2 = p.context(open, '/etc/hostname', 'rb')
>>> p is not p2
True
>>> p3 = p2.label('one with label')
>>> p3 is not p2
True
>>> isinstance(p, param) and isinstance(p2, param) and isinstance(p3, param)
True

Now, what about using @expand as a class decoratorw?

It's similar to using @expand as a method decorator, except that you
must remeber to place the @parametrize decorator as the topmost (the
outer) decorator (above all @expand decorators).

Also, when using @expand as a class decorator, you can -- or should,
if you want to prevent the library from hackish interpreter stack
introspection (which may not work with some Python implementations) --
pass the 'into' keyword argument into the @parametrize decorator.
The argument specifies when the generated subclasses of the test case
class should be placed; the attribute value should be either a mapping
or a (non-read-only) module, or a name of such a module.

For example, let's use a dict as the 'into' argument for the
@parametrize decorator:

>>> into_dict = {}
>>>
>>> params_with_contexts = paramseq([
...     param(save='', load=''),
...     param(save='abc', load='abc'),
... ]).context(NamedTemporaryFile, 'w+t')
>>>
>>> useless_data = [
...     param('foo', b=42),
...     param('foo', b=433)]
>>>
>>> @parametrize(into=into_dict)
... @expand(params_with_contexts)
... @expand(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         # note: test class params, context targets and label are
...         # accessible as instance attributes (not as test arguments):
...         self.file = self.context_targets[0]
...         assert self.save == self.load, 'params should be equal'
...         assert self.params == ('foo',) and self.b in (42, 433)
...         assert 'foo' in self.label
...         # (note: on Python 2.7+ we could resign from using contexts
...         # and just use unittest.TestCase.addCleanup() here...)
...
...     @expand([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
"TestSaveLoad__<'foo',b=42, load='',save=''>"
"TestSaveLoad__<'foo',b=42, load='abc',save='abc'>"
"TestSaveLoad__<'foo',b=433, load='',save=''>"
"TestSaveLoad__<'foo',b=433, load='abc',save='abc'>"
>>>
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__<suffix=' '> (..._<'foo',b=42, load='',save=''>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='',save=''>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='',save=''>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='',save=''>) ... ok
test_save_load__<suffix=' '> (..._<'foo',b=433, load='abc',save='abc'>) ... ok
test_save_load__<suffix='XX'> (..._<'foo',b=433, load='abc',save='abc'>) ... ok
...
Ran 8 tests...
OK

(As you see, you can combine @expand as class decorator(s) with @expand
as method decorator(s) -- you will obtain tests parametrized with the
cartesian product of the involved parameter collections.)

Contexts are, obviously, properly dispatched also when errors occur:

>>> into_dict = {}
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
>>> @parametrize(into=into_dict)
... @expand(err_params)
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
...
Ran 9 tests...
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

(Note: contexts attached to test *class* params [in contrast to those
attached to test *method* params] are dispatched within setUp()
and (if applicable) tearDown() -- so setUp() and tearDown() *are*
affected by errors related to those contexts.  On the other hand,
context finalization (__exit__) is *not* affected by any exceptions
from actual test methods.)

One could ask: "What the @parametrize decorator does with the original
objects (classes or methods) decorated with @expand?".  They cannot be
left where they are because, without parametrization, they are not valid
tests (but rather kind of test templates).

Because of that, they are always replaced with substitute objects:

>>> TestSaveLoad                                   # doctest: +ELLIPSIS
<...Substitute object at 0x...>

>>> TestSaveLoad.actual_object                     # doctest: +ELLIPSIS
<class '...TestSaveLoad'>

>>> (set(dir(TestSaveLoad.actual_object)) - set(['__call__'])
...  ).issubset(dir(TestSaveLoad))
True

>>> TestSaveLoad.test_save_load                    # doctest: +ELLIPSIS
<...Substitute object at 0x...>

>>> TestSaveLoad.test_save_load.actual_object      # doctest: +ELLIPSIS
<...test_save_load...>

(As you see, such a substitute object is kind of a non-callable proxy to
the actual class/method).

Below -- another example of using @expand as a class decorator: with
@parametrize's 'into' being set to a module object:

>>> import types
>>> module = types.ModuleType('_my_weird_module')
>>>
>>> @parametrize(into=module)
... @expand(params_with_contexts)
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
...         name, getattr(module, name)  # doctest: +ELLIPSIS
...
("TestSaveLoad__<load='',save=''>", ...TestSaveLoad__<load='',save=''>...)
("TestSaveLoad__<load='abc',save='abc'>", ...TestSaveLoad__<load='abc'...)
>>>
>>> TestSaveLoad__1 = getattr(module, "TestSaveLoad__<load='',save=''>")
>>> TestSaveLoad__2 = getattr(module, "TestSaveLoad__<load='abc',save='abc'>")
>>>
>>> run_tests(TestSaveLoad__1, TestSaveLoad__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoad__<load='',save=''>) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>) ... ok
...
Ran 2 tests...
OK

...and with 'into' being set to an importable module name:

>>> module = types.ModuleType('_my_weird_module')
>>> sys.modules['_my_weird_module'] = module
>>>
>>> @parametrize(into='_my_weird_module')
... @expand(params_with_contexts)
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
...         name, getattr(module, name)  # doctest: +ELLIPSIS
...
("TestSaveLoad__<load='',save=''>", ...TestSaveLoad__<load='',save=''>...)
("TestSaveLoad__<load='abc',save='abc'>", ...TestSaveLoad__<load='abc'...)
>>>
>>> TestSaveLoad__1 = getattr(module, "TestSaveLoad__<load='',save=''>")
>>> TestSaveLoad__2 = getattr(module, "TestSaveLoad__<load='abc',save='abc'>")
>>>
>>> run_tests(TestSaveLoad__1, TestSaveLoad__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoad__<load='',save=''>) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>) ... ok
...
Ran 2 tests...
OK

...and with 'into' not specified, and implicitly inferred by the library
(this variant works well with CPython and PyPy but may not work with
Python implementations that do not support stack frame introspection):

>>> # first, some magic -- needed only for doctests
>>> this = types.ModuleType('_my_weird_module')
>>> sys.modules['_my_weird_module'] = this
>>> __name__ = this.__name__
>>>
>>> @parametrize
... @expand(params_with_contexts)
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
>>> for name in dir(this):
...     if not name.startswith('__'):
...         name, getattr(this, name)  # doctest: +ELLIPSIS
...
("TestSaveLoad__<load='',save=''>", ...TestSaveLoad__<load='',save=''>...)
("TestSaveLoad__<load='abc',save='abc'>", ...TestSaveLoad__<load='abc'...)
>>>
>>> TestSaveLoad__1 = getattr(this, "TestSaveLoad__<load='',save=''>")
>>> TestSaveLoad__2 = getattr(this, "TestSaveLoad__<load='abc',save='abc'>")
>>>
>>> run_tests(TestSaveLoad__1, TestSaveLoad__2)  # doctest: +ELLIPSIS
test_save_load (...TestSaveLoad__<load='',save=''>) ... ok
test_save_load (...TestSaveLoad__<load='abc',save='abc'>) ... ok
...
Ran 2 tests...
OK

One more thing: if you don't like how parametrized method names or class
names are formatted -- you can customize it globally by:

* setting parametrize.name_pattern to a '{field}'-formattable pattern
  containing one or more of the fields: 'base_name' (name of the
  original test method or class), 'label' (parameter representation
  or specified label), 'count' (consecutive number of generated
  parametrized method or class);

and/or

* setting parametrize.name_formatter to any object whose format() method
  signature complies with the signature of string.Formatter.format().

For example:

>>> parametrize.name_pattern = '{base_name}__parametrized_{count}'
>>>
>>> into_dict = {}
>>>
>>> @parametrize(into=into_dict)
... @expand(params_with_contexts)
... @expand(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     @expand([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
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
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_1) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_1) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_2) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_2) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_3) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_3) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_4) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_4) ... ok
...
Ran 8 tests...
OK

...or, let's say:

>>> import string
>>> class SillyFormatter(string.Formatter):
...     def format(self, format_string, *args, **kwargs):
...         label = kwargs.get('label', '')
...         if '42' in label:
...             return '<{0}>'.format(label)
...         else:
...             return super(SillyFormatter,
...                          self).format(format_string, *args, **kwargs)
...
>>> parametrize.name_formatter = SillyFormatter()
>>>
>>> into_dict = {}
>>>
>>> @parametrize(into=into_dict)
... @expand(params_with_contexts)
... @expand(useless_data)
... class TestSaveLoad(unittest.TestCase):
...
...     def setUp(self):
...         self.file = self.context_targets[0]
...
...     @expand([param(suffix=' '), param(suffix='XX')])
...     def test_save_load(self, suffix):
...         self.file.write(self.save + suffix)
...         self.file.seek(0)
...         load_actually = self.file.read()
...         self.assertEqual(load_actually, self.load + suffix)
...
>>> for name in sorted(into_dict):  # doctest: +ELLIPSIS
...     name
...
"<'foo',b=42, load='',save=''>"
"<'foo',b=42, load='abc',save='abc'>"
'TestSaveLoad__parametrized_3'
'TestSaveLoad__parametrized_4'
>>>
>>> test_classes = [into_dict[name] for name in sorted(into_dict)]
>>> run_tests(*test_classes)  # doctest: +ELLIPSIS
test_save_load__parametrized_1 (...<'foo',b=42, load='',save=''>) ... ok
test_save_load__parametrized_2 (...<'foo',b=42, load='',save=''>) ... ok
test_save_load__parametrized_1 (...<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__parametrized_2 (...<'foo',b=42, load='abc',save='abc'>) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_3) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_3) ... ok
test_save_load__parametrized_1 (...TestSaveLoad__parametrized_4) ... ok
test_save_load__parametrized_2 (...TestSaveLoad__parametrized_4) ... ok
...
Ran 8 tests...
OK

You can reset these two options to defaults by setting that attributes
to None:

>>> parametrize.name_pattern = None
>>> parametrize.name_formatter = None

Also, note that the library automatically does its best to avoid name
clashes -- when it detects a clash it adds a suffix to a newly formatted
name, e.g.:

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
>>> @parametrize(into=into_dict)
... @expand(useless_data)
... @setting_attrs(extra_attrs)
... class Test_is_even(unittest.TestCase):
...
...     @expand([
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
...
Ran 12 tests...
OK
"""

from unittest_parametrize._internal import (
    expand,
    parametrize,
    Param as param,
    ParamSeq as paramseq,
)

__all__ = (
    'expand',
    'parametrize',
    'param',
    'paramseq',
)


expand.__module__ = __name__
parametrize.__module__ = __name__
param.__module__ = __name__
paramseq.__module__ = __name__

param.__name__ = 'param'
if hasattr(param, '__qualname__'):
    # relevant to Python 3.3+
    param.__qualname__ = param.__name__

paramseq.__name__ = 'paramseq'
if hasattr(paramseq, '__qualname__'):
    # relevant to Python 3.3+
    paramseq.__qualname__ = paramseq.__name__
