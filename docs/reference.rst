Module Contents
===============

.. module:: unittest_expander

The module :mod:`unittest_expander` contains the following functions
and classes.

(See: :doc:`narrative_documentation` for descriptions and examples of
their usage...)


The :func:`expand` class decorator
----------------------------------

.. decorator:: expand(*, into=globals())

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

   The class has the following methods:

   .. method:: __add__(other)

       Returns a new :class:`paramseq` instance (concatenates the
       current instance with *other*).

   .. method:: __radd__(other)

       Returns a new :class:`paramseq` instance (concatenates *other*
       with the current instance).

   .. method:: context(context_manager_factory, *its_args, **its_kwargs)

       Returns a new :class:`paramseq` instance contaning the same
       items as the current instance -- but each item with the
       specified context factory attached.

The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   The class has the following methods:

   .. method:: context(context_manager_factory, *its_args, **its_kwargs)

       Returns a new :class:`param` instance being a clone of the
       current instance, with the specified context factory attached.

   .. method:: label(text)

       Returns a new :class:`param` instance being a clone of the
       current instance, with the specified label text attached.

The :class:`Substitute` class
-----------------------------

.. class:: Substitute(actual_object)

   .. attribute:: actual_object
