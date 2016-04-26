Module Contents
===============

.. module:: unittest_expander

The module :mod:`unittest_expander` contains the following functions and
classes.

(See: :doc:`narrative_documentation` -- for descriptions and examples of
their usage...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand(*, into=globals())

   The public interface includes the following attributes:

   .. attribute:: expand.global_name_pattern

   .. attribute:: expand.global_name_formatter

The :func:`foreach` method/class decorator
------------------------------------------

.. decorator:: foreach(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a sequence (``isinstance(param_collection, collections.Sequence)``
     returns :obj:`True`) but *not* a string,
   * a mapping (``isinstance(param_collection, collections.Mapping)``
     returns :obj:`True`),
   * a set (``isinstance(param_collection, collections.Set)`` returns
     :obj:`True`),
   * a callable (``callable(param_collection)`` returns :obj:`True`)
     that returns an iterable object (such as generator).

   Each item of a parameter collection is one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of the tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: the object).

*or*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

   Total number of given arguments (positional and/or keyword ones) must
   be greater than 1.  Each argument will be treated as a parameter
   collection item (see above); for keyword arguments, their names will
   be used to call :meth:`param.label`.

The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

   *param_collection* must be a parameter collection -- that is, one of:

   * a :class:`paramseq` instance,
   * a sequence (``isinstance(param_collection, collections.Sequence)``
     returns :obj:`True`) but *not* a string,
   * a mapping (``isinstance(param_collection, collections.Mapping)``
     returns :obj:`True`),
   * a set (``isinstance(param_collection, collections.Set)`` returns
     :obj:`True`),
   * a callable (``callable(param_collection)`` returns :obj:`True`)
     that returns an iterable object (such as generator).

   Each item of a parameter collection is one of:

   * a :class:`param` instance,
   * a :class:`tuple` (converted automatically to a :class:`param`
     that contains the items of the tuple),
   * any other object (converted automatically to a :class:`param`
     that contains only one item: the object).

*or*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

   Total number of given arguments (positional and/or keyword ones) must
   be greater than 1.  Each argument will be treated as a parameter
   collection item (see above); for keyword arguments, their names will
   be used to call :meth:`param.label`.

   The public interface of instances of the class includes the following
   methods:

   .. method:: __add__(other)

       Returns a new :class:`paramseq` instance (being a result of
       concatenation of the current :class:`paramseq` instance and the
       *other* parameter collection).

   .. method:: __radd__(other)

       Returns a new :class:`paramseq` instance (being a result of
       concatenation of the *other* parameter collection and the current
       :class:`paramseq` instance).

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       __enable_exc_suppress__=False)

       Returns a new :class:`paramseq` instance contaning clones of the
       items of the current instance -- each cloned with
       :meth:`param.context` called with the given arguments.

The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   The public interface of instances of the class includes the following
   methods:

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       __enable_exc_suppress__=False)

       Returns a new :class:`param` instance being a clone of the
       current instance, with the specified context manager factory (and
       its arguments) attached.

       By default, the possibility to suppress exceptions by returning a
       true value from context manager's :meth:`__exit__` is disabled
       (exceptions are propagated even if :meth:`__exit__` returns
       :obj:`True`); to enable this possibility specify the
       *__enable_exc_suppress__* keyword argument as :obj:`True`.

   .. method:: label(text)

       Returns a new :class:`param` instance being a clone of the
       current instance, with the specified label text attached.

The :class:`Substitute` class
-----------------------------

.. class:: Substitute(actual_object)

   The public interface of instances of the class includes the following
   attribute (besides all attributes of the proxied object -- see:
   :ref:`about-substitute`):

   .. attribute:: actual_object

      The proxied object.
