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

   The public interface includes also the following attributes:

   .. attribute:: expand.global_name_pattern

   .. attribute:: expand.global_name_formatter

The :func:`foreach` method/class decorator
------------------------------------------

.. decorator:: foreach(param_collection)

*or*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

*or*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

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

       Returns a new :class:`paramseq` instance contaning the same items
       as the current instance -- but each item with the specified
       context factory attached.

The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   The public interface of instances of the class includes the following
   methods:

   .. method:: context(context_manager_factory, \
                       *its_args, **its_kwargs, \
                       __enable_exc_suppress__=False)

       Returns a new :class:`param` instance being a clone of the
       current instance, with the specified context factory attached.

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
