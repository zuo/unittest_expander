Module Contents
===============

.. module:: unittest_expander

The module :mod:`unittest_expander`'s public interface consists of the
following functions and classes.

(See: :doc:`narrative_documentation` -- for a much richer description of
them, including a lot of usage examples...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand

*or*

.. decorator:: expand(*, into=globals())

   .. deprecated:: 0.4.0

      The *into* argument will become *illegal* in the version *0.5.0*.

   ———

   The public interface this decorator provides includes also the
   following attributes, making it possible to :ref:`change the way
   of formatting names <custom-name-formatting>` of generated test
   methods/classes:

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

   .. deprecated:: 0.4.0

      A parameter collection being a tuple (i.e., an instance of
      the built-in type :class:`tuple` or of a subclass of it, e.g.,
      a *named tuple*) will become *illegal* in the version *0.5.0*
      (note that this deprecation concerns tuples used as *parameter
      collections* themselves, *not* as *items* of parameter
      collections; the latter are -- and will be -- perfectly OK).

   Each item of the parameter collection should be one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of that tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: that object).

*or*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

   The total number of given arguments (positional and/or keyword ones)
   must be greater than 1.  Each argument will be treated as a parameter
   collection's *item* (see above); for keyword arguments, their names
   will be used to :meth:`~param.label` them.

   ———

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

      A parameter collection being a tuple (i.e., an instance of
      the built-in type :class:`tuple` or of a subclass of it, e.g.,
      a *named tuple*) will become *illegal* in the version *0.5.0*
      (note that this deprecation concerns tuples used as *parameter
      collections* themselves, *not* as *items* of parameter
      collections; the latter are -- and will be -- perfectly OK).

   Each item of the parameter collection should be one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of that tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: that object).

*or*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

   The total number of given arguments (positional and/or keyword ones)
   must be greater than 1.  Each argument will be treated as a parameter
   collection's *item* (see above); for keyword arguments, their names
   will be used to :meth:`~param.label` them.

   ———

   The public interface this class provides includes the following
   instance methods:

   .. method:: __add__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of the current :class:`paramseq` instance and given
      *param_collection* (see the description of the :class:`paramseq`
      constructor's argument *param_collection*...).

   .. method:: __radd__(param_collection)

      Returns a new :class:`paramseq` instance -- being a result of
      concatenation of given *param_collection* (see the description of
      the :class:`paramseq` constructor's argument *param_collection*...)
      and the current :class:`paramseq` instance.

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       _enable_exc_suppress_=False)

      Returns a new :class:`paramseq` instance contaning clones
      of the items of the current instance -- each cloned with
      :meth:`param.context` (see below) called with the given
      arguments.


The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   *args* and *kwargs* specify actual parameters to be passed to test
   method call(s).

   ———

   The public interface this class provides includes the following
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

   *actual_object* is the object to be wrapped (proxied).

   ———

   The public interface this class provides includes the following
   instance attribute (besides nearly all attributes of the proxied
   object -- see: :ref:`about-substitute`):

   .. attribute:: actual_object

      The proxied object itself (not wrapped).
