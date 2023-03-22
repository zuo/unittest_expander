Module Contents
===============

.. module:: unittest_expander

The public interface of the :mod:`unittest_expander` module consists of
the following functions, classes and constants.

(See: :doc:`narrative_documentation` -- for a much richer description of
most of them, including a lot of usage examples...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand

   Apply this decorator to a *test class* to generate actual
   *parametrized test methods*, i.e., to "expand" parameter collections
   which have been bound (by applying :func:`foreach`) to original *test
   methods*.

   ———

   The public interface of :func:`expand` includes also the following
   attributes (making it possible to :ref:`customize how names of
   parametrized test methods are generated <custom-name-formatting>`):

   .. attribute:: expand.global_name_pattern

   .. attribute:: expand.global_name_formatter


The :func:`foreach` method decorator
------------------------------------

.. decorator:: foreach(param_collection)

*or*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

   Call this function, specifying parameter collections to be bound to a
   *test method*, and then apply the resultant decorator to that method
   (only then it will be possible -- by applying :func:`expand` to the
   *test class* owning the method -- to generate actual *parametrized
   test methods*).

   To learn what arguments need to be passed to the :func:`foreach`
   call, see the description of :class:`paramseq` (note that the call
   signatures of :func:`foreach` and the :class:`paramseq`'s constructor
   are the same).


The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a *sequence* **not being** a :class:`tuple`, *text string* or
     :class:`bytes`/:class:`bytearray` (in other words, such an object
     for whom ``isinstance(obj, collections.abc.Sequence) and not
     isinstance(obj, (tuple, str, bytes, bytearray))`` returns
     :obj:`True` in Python 3) -- for example, a :class:`list`,
   * a *mapping* (i.e., such an object that ``isinstance(obj,
     collections.abc.Mapping)`` returns :obj:`True` in Python 3)
     -- for example, a :class:`dict`,
   * a *set* (i.e., such an object that ``isinstance(obj,
     collections.abc.Set)`` returns :obj:`True` in Python 3)
     -- for example, a :class:`set` or :class:`frozenset`,
   * a *callable* (i.e., such an object that ``callable(obj)`` returns
     :obj:`True`) which is supposed: to accept one positional argument
     (the *test class*) or no arguments at all, and to return an
     *iterable* object (i.e., an object that could be used as a ``for``
     loop's subject, able to yield consecutive items) -- for example, a
     :term:`generator`.

   Each *item* of a parameter collection is supposed to be:

   * a :class:`param` instance,
   * a :class:`tuple` (to be converted automatically to a :class:`param`
     which will contain parameter values being the items of that tuple),
   * any other object (to be converted automatically to a :class:`param`
     which will contain only one parameter value: that object).

*or*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

   The total number of given arguments (positional and/or keyword ones)
   must be greater than 1.  Each argument will be treated as a parameter
   collection's *item* (see above); for each keyword argument (if any),
   its name will be used to :meth:`~param.label` the *item* it refers to.

   ———

   A :class:`paramseq` instance is the canonical form of a parameter
   collection.

   The public interface provided by this class includes the following
   instance methods:

   .. method:: __add__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the :class:`paramseq` instance we operate on
      and the given *param_collection* (see the description of the
      :class:`paramseq` constructor's argument *param_collection*...).

   .. method:: __radd__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the given *param_collection* (see the description
      of the :class:`paramseq` constructor's argument
      *param_collection*...) and the :class:`paramseq` instance we
      operate on.

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`paramseq` instance containing clones
      of the items of the instance we operate on -- each cloned with a
      :meth:`param.context` call (see below), to which all given
      arguments are passed.


The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   *args* and *kwargs* specify actual (positional and keyword) arguments
   to be passed to test method call(s).

   ———

   A :class:`param` instance is the canonical form of a parameter
   collection's *item*. It represents :ref:`a single combination of test
   parameter values <param-basics>`.

   The public interface provided by this class includes the following
   instance methods:

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`param` instance being a clone of the
      the instance we operate on, with the specified context manager
      factory (and its arguments) attached.

      By default, the possibility to suppress exceptions by returning
      a *true* value from context manager's :meth:`__exit__` is
      :ref:`disabled <contexts-cannot-suppress-exceptions>`
      (exceptions are propagated even if :meth:`__exit__` returns
      :obj:`True`); to enable this possibility you need to set the
      *_enable_exc_suppress_* keyword argument to :obj:`True`.

   .. method:: label(text)

      Returns a new :class:`param` instance being a clone of the
      instance we operate on, with the specified textual label attached.


Non-essential constants and classes
-----------------------------------

.. data:: __version__

   The version of :mod:`unittest_expander` as a :pep:`440`-compliant
   identifier (being a :class:`str`).


.. class:: Substitute(actual_object)

   *actual_object* is the object :ref:`to be proxied <about-substitute>`
   (typically, it is a test method, previously decorated with
   :func:`foreach`).

   Apart from exposing in a transparent way nearly all attributes
   of the proxied object, the public interface provided by the
   :class:`Substitute` class includes the following instance attribute:

   .. attribute:: actual_object

      The proxied object itself (unwrapped).

   .. note::

      :class:`Substitute` instances are *not* callable.
