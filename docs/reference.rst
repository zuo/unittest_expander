Module Contents
===============

.. module:: unittest_expander

The module :mod:`unittest_expander` contains the following functions and classes:

The :func:`expand` class decorator
----------------------------------

.. decorator:: expand(*, into=globals())

.. attribute:: expand.global_name_pattern

.. attribute:: expand.global_name_formatter

The :func:`foreach` method/class decorator
------------------------------------------

.. decorator:: foreach(param_collection)

*or:*

.. decorator:: foreach(*param_collection_items, **param_collection_labeled_items)

The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection)

*or:*

.. class:: paramseq(*param_collection_items, **param_collection_labeled_items)

   The class has the following methods:

   .. method:: __add__(other) -> new paramseq instance

   .. method:: __radd__(other) -> new paramseq instance

   .. method:: context(context_manager_factory, *its_args, **its_kwargs) -> new paramseq instance

The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   The class has the following methods:

   .. method:: context(context_manager_factory, *its_args, **its_kwargs) -> new param instance

   .. method:: label(text) -> new param instance

The :class:`Substitute` class
-----------------------------

.. class:: Substitute(actual_object)

   .. attribute:: actual_object
