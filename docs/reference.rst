Module Contents
===============

.. module:: unittest_expander

The public interface of the :mod:`unittest_expander` module consists of
the following functions, classes, objects and constants.

(See: :doc:`narrative_documentation` -- for a much richer description of
most of them, including a lot of usage examples...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand

   Apply this decorator to a *test class* to generate actual
   *parametrized test methods*, i.e., to "expand" parameter collections
   which have been bound (by applying :func:`foreach`) to original *test
   methods*.

   ―

   The public interface of :func:`expand` includes also the attributes
   described below.

   Two of them make it possible to :ref:`customize how names of
   parametrized test methods are generated <custom-name-formatting>`:

   .. attribute:: expand.global_name_pattern

      :type: :class:`str` or :obj:`None`
      :value: :obj:`None` (use the default pattern)

   .. attribute:: expand.global_name_formatter

      :type: :class:`string.Formatter`-like object or :obj:`None`
      :value: :obj:`None` (use the default formatter)

   Other two allow -- respectively -- to :ref:`switch the context
   ordering style <context-order>`, and to decide whether :ref:`a
   certain deprecated, signature-introspection-based feature
   <label-and-context-targets-as-kwargs>` shall be enabled:

   .. attribute:: expand.legacy_context_ordering

      :type: :class:`bool`
      :value: :obj:`True`

   .. attribute:: expand.legacy_signature_introspection

      :type: :class:`bool`
      :value: :obj:`True`

   .. warning::

      For each of the last two attributes, :obj:`True` (the default
      value) dictates a deprecated (legacy) behavior, whereas only
      :obj:`False` is compatible with future versions of
      *unittest_expander*.


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

   To learn more about what needs to be passed to :func:`foreach`, see
   the description (below) of the :class:`paramseq`'s constructor (note
   that the call signatures of :func:`foreach` and that constructor are
   the same).


The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a *sequence* **not being** a
     :class:`tuple`/:class:`str`/:class:`unicode`/:class:`bytes`/:class:`bytearray`
     (in other words, such an object for whom ``isinstance(obj,
     collections.abc.Sequence) and not isinstance(obj, (tuple,
     str, bytes, bytearray))`` returns :obj:`True` in Python 3)
     -- for example, a :class:`list`,
   * a *mapping* (i.e., such an object that ``isinstance(obj,
     collections.abc.Mapping)`` returns :obj:`True` in Python 3)
     -- for example, a :class:`dict`,
   * a *set* (i.e., such an object that ``isinstance(obj,
     collections.abc.Set)`` returns :obj:`True` in Python 3)
     -- for example, a :class:`set` or :class:`frozenset`,
   * a *callable* (i.e., such an object that ``callable(obj)`` returns
     :obj:`True`) which is supposed to:

     * accept one positional argument (the *test class*) or
       no arguments at all,
     * return an *iterable* object (i.e., an object that could be
       used as a ``for`` loop's subject, able to yield consecutive
       items)

     -- for example, a :term:`generator` function.

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

   ―

   A :class:`paramseq` instance is the canonical form of a parameter
   collection.

   Its public interface includes the following methods:

   .. method:: __add__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the :class:`paramseq` instance we operate on
      and the given *param_collection* (see the above description of the
      :class:`paramseq` constructor's argument *param_collection*...).

   .. method:: __radd__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the given *param_collection* (see the above
      description of the :class:`paramseq` constructor's argument
      *param_collection*...) and the :class:`paramseq` instance we
      operate on.

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`paramseq` instance containing clones
      of the items of the instance we operate on -- each cloned with a
      :meth:`param.context` call (see below...) to which all given
      arguments are passed.


The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   *args* and *kwargs* specify actual (positional and keyword) arguments
   to be passed to test method call(s).

   ―

   A :class:`param` instance is the canonical form of a parameter
   collection's *item*. It represents :ref:`a single combination of test
   parameter values <param-basics>`.

   Its public interface includes the following methods:

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


The :obj:`current` special object
---------------------------------

.. data:: current

   A special singleton object which, when used during execution of a
   parametrized test method, provides access (in a `thread-local`_
   manner) to the following properties of the (currently executed) test:

   .. attribute:: current.label

      :type: :class:`str`
      :value: the :ref:`test's label <test-labels>` (which was
              automatically generated or explicitly specified with
              :meth:`param.label`...)

   .. attribute:: current.context_targets

      :type: :class:`~collections.abc.Sequence`
      :value: the :ref:`test contexts' as-targets <test-context-targets>`
              (i.e., objects returned by :meth:`__enter__` of each of the
              context managers which were specified with
              :meth:`param.context`...)

   .. attribute:: current.all_args

      :type: :class:`~collections.abc.Sequence`
      :value: all *positional arguments* obtained by the currently
              executed parametrized test method (in particular,
              including all positional arguments which were passed
              to the :class:`param` constructor...)

   .. attribute:: current.all_kwargs

      :type: :class:`~collections.abc.Mapping`
      :value: all *keyword arguments* obtained by the currently
              executed parametrized test method (in particular,
              including all keyword arguments which were passed
              to the :class:`param` constructor...)

   .. attribute:: current.count

      :type: :class:`int`
      :value: the consecutive number (within a single application of
              :func:`expand`) of the generated parametrized test method

   .. attribute:: current.base_name

      :type: :class:`str`
      :value: the name of the original (non-parametrized) test method

   .. attribute:: current.base_obj

      :type: :data:`function <types.FunctionType>`
      :value: the original (non-parametrized) test method itself

.. _thread-local: https://docs.python.org/library/threading.html#thread-local-data


Non-essential constants and classes
-----------------------------------

.. data:: __version__

   The version of :mod:`unittest_expander` as a :class:`str` being a
   :pep:`440`-compliant identifier.


.. class:: Substitute(actual_object)

   A kind of attribute-access-proxying wrapper, :ref:`automatically
   applied <about-substitute>` by the machinery of :func:`expand` to
   each test method previously decorated with :func:`foreach`.

   The sole constructor argument (*actual_object*) is the object
   (typically, a test method) to be proxied.

   Apart from exposing in a transparent way nearly all attributes
   of the proxied object, the public interface of a :class:`Substitute`
   includes the following instance attribute:

   .. attribute:: actual_object

      The proxied object itself (unwrapped).

   .. note::

      A :class:`Substitute` instance is *never* callable -- even though
      (typically) the proxied object is.
