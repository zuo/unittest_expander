Module Contents
===============

.. module:: unittest_expander

The module :mod:`unittest_expander`'s public interface consists of the
following functions, classes and constants.

(See: :doc:`narrative_documentation` -- for a much richer description of
most of them, including a lot of usage examples...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand

*or*

.. decorator:: expand(*, into=globals())

   .. deprecated:: 0.4.0

      The *into* argument will become *illegal* in the version *0.5.0*.

   ———

   This decorator is intended to be applied to *test classes*: doing
   that causes that test parameters -- previously attached to related
   test methods (and/or classes) by decorating them with :func:`foreach`
   -- are "expanded", that is, actual parametrized versions of those
   methods (and/or classes) are generated.

   The public interface provided by :func:`expand` includes also the
   following attributes (making it possible to :ref:`customize how
   names of parametrized test methods and classes are generated
   <custom-name-formatting>`):

   .. attribute:: expand.global_name_pattern

   .. attribute:: expand.global_name_formatter


The :func:`foreach` method/class decorator
------------------------------------------

.. decorator:: foreach(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a sequence (i.e., such an object that
     ``isinstance(obj, collections.abc.Sequence)`` returns :obj:`True`)
     but *not* a string,
   * a mapping (i.e., such an object that
     ``isinstance(obj, collections.abc.Mapping)`` returns :obj:`True`),
   * a set (i.e., such an object that
     ``isinstance(obj, collections.abc.Set)`` returns :obj:`True`),
   * a callable (i.e., such an object that ``callable(obj)`` returns
     :obj:`True`) that returns an iterable object (for example, a
     generator/iterator).

   Any valid parameter collection will be, under the hood, automatically
   converted to a :class:`paramseq`.

   .. deprecated:: 0.4.0

      A parameter collection given as a tuple (i.e., an instance of
      the built-in type :class:`tuple` or of a subclass of it, e.g.,
      a *named tuple*) will become *illegal* in the version *0.5.0*
      (note that this deprecation concerns tuples used as *parameter
      collections* themselves, *not* as *items* of parameter
      collections; the latter are -- and will be -- perfectly OK).
      As a parameter collection, instead of a tuple, use another type
      (e.g., a :class:`list`).

   Each item of a parameter collection should be one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of that tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: that object).

*or*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

   The total number of given arguments (positional and/or keyword ones)
   must be greater than 1.  Each argument will be treated as a parameter
   collection's *item* (see above); for each keyword argument (if any),
   its name will be used to :meth:`~param.label` the *item* it refers to.

   ———

   This decorator is intended to be applied to test *methods* and/or
   test *classes* -- to attach to those methods (or classes) the test
   parameters from the specified parameter collection (only then it is
   possible to generate, by using :func:`expand`, actual parametrized
   methods and/or classes...).

   .. deprecated:: 0.4.0

      Support for decorating test *classes* with :func:`foreach` will be
      *removed* in the version *0.5.0*.


The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a sequence (i.e., such an object that
     ``isinstance(obj, collections.abc.Sequence)`` returns :obj:`True`)
     but *not* a string,
   * a mapping (i.e., such an object that
     ``isinstance(obj, collections.abc.Mapping)`` returns :obj:`True`),
   * a set (i.e., such an object that
     ``isinstance(obj, collections.abc.Set)`` returns :obj:`True`),
   * a callable (i.e., such an object that ``callable(obj)`` returns
     :obj:`True`) that returns an iterable object (for example, a
     generator/iterator).

   .. deprecated:: 0.4.0

      A parameter collection given as a tuple (i.e., an instance of
      the built-in type :class:`tuple` or of a subclass of it, e.g.,
      a *named tuple*) will become *illegal* in the version *0.5.0*
      (note that this deprecation concerns tuples used as *parameter
      collections* themselves, *not* as *items* of parameter
      collections; the latter are -- and will be -- perfectly OK).
      As a parameter collection, instead of a tuple, use another type
      (e.g., a :class:`list`).

   Each item of a parameter collection should be one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of that tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: that object).

*or*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

   The total number of given arguments (positional and/or keyword ones)
   must be greater than 1.  Each argument will be treated as a parameter
   collection's *item* (see above); for each keyword argument (if any),
   its name will be used to :meth:`~param.label` the *item* it refers to.

   ———

   A :class:`paramseq` object is the canonical form of a parameter
   collection -- whose items are :class:`param` objects.

   The public interface provided by this class includes the following
   instance methods:

   .. method:: __add__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the current :class:`paramseq` instance and given
      *param_collection* (see the description of the :class:`paramseq`
      constructor's argument *param_collection*...).

      .. deprecated:: 0.4.0

         *param_collection* being a tuple will become *illegal* in the
         version *0.5.0*.

   .. method:: __radd__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of given *param_collection* (see the description of
      the :class:`paramseq` constructor's argument *param_collection*...)
      and the current :class:`paramseq` instance.

      .. deprecated:: 0.4.0

         *param_collection* being a tuple will become *illegal* in the
         version *0.5.0*.

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`paramseq` instance contaning clones
      of the items of the current instance -- each cloned with a
      :meth:`param.context` call (see below), to which all given
      arguments are passed.


The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   *args* and *kwargs* specify actual parameters to be passed to test
   method call(s).

   ———

   A :class:`param` object is the canonical form of a parameter
   collection's *item* -- which represents a single :ref:`combination
   of test parameter values <param-basics>`.

   The public interface provided by this class includes the following
   instance methods:

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`param` instance being a clone of the
      current instance, with the specified context manager factory
      (and its arguments) attached.

      By default, the possibility to suppress exceptions by returning
      a true value from context manager's :meth:`__exit__` is disabled
      (exceptions are propagated even if :meth:`__exit__` returns
      :obj:`True`); to enable this possibility you need to set the
      *_enable_exc_suppress_* keyword argument to :obj:`True`.

   .. method:: label(text)

      Returns a new :class:`param` instance being a clone of the
      current instance, with the specified label text attached.


The :class:`Substitute` class
-----------------------------

.. class:: Substitute(actual_object)

   *actual_object* is the object :ref:`to be proxied <about-substitute>`.

   ———

   Apart from exposing in a transparent way nearly all attributes of
   the proxied object (also methods -- with a notable exception of
   :meth:`__call__`), the public interface provided by this class
   includes the following instance attribute:

   .. attribute:: actual_object

      The proxied object itself (unwrapped).


The :data:`__version__` constant
--------------------------------

.. data:: __version__

   The version of :mod:`unittest_expander` as a :pep:`440`-compliant
   identifier (being a :class:`str`).
