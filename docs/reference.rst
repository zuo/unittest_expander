Library Reference
=================

.. module:: unittest_expander

The module :mod:`unittest_expander` contains the following functions and classes:

The :func:`expand` class decorator
----------------------------------

.. decorator:: expand(*[, into=globals()])

.. attribute:: expand.global_name_pattern

.. attribute:: expand.global_name_formatter

The :func:`foreach` method/class decorator
------------------------------------------

.. decorator:: foreach(param_collection)

The :class:`param` class
------------------------

.. class:: param(*args, **kwargs)

   .. method:: context(context_manager_factory, *its_args, **its_kwargs)

   .. method:: label(text)

The :class:`paramseq` class
---------------------------

.. class:: paramseq(param_collection | **kwargs)

   .. method:: __add__(other)

   .. method:: context(context_manager_factory, *its_args, **its_kwargs)

The :class:`Substitute` class
-----------------------------

.. class:: Substitute(actual_object)

   .. attribute:: actual_object
