Changes
=======

0.3.0 (2014-08-17)
------------------

Improved signatures of the **foreach()** decorator and the
**paramseq** constructor: they take either exactly one positional
argument which is a test parameter collection (as previously: a
sequence/mapping/set or a **paramseq** instance, or a callable
returning an iterable...), or *any number of positional and/or keyword
arguments being test parameters* (singular parameter values, tuples of
parameter values or **param** instances...).  For example:
``@foreach([1, 42])`` can now also be spelled as: ``@foreach(1, 42)``.

Several testing/documentation-related updates, fixes and improvements.

0.2.1 (2014-08-12)
------------------

Important internal fixes (of 0.2.0-related regressions) and cleanups:

* a setup-breaking bug in *setup.py* has been fixed and some
  setup-related cleanups have been made as well;
* the configuration of Sphinx (package docs generator tool) has been
  fixed.

0.2.0 (2014-08-11)
------------------

Now **unittest_expander** is a one-file module, not a directory-based
package.

Internal changes:

* some documentation improvements and updates;
* some library setup improvements and refactorings.

0.1.2 (2014-08-01)
------------------

The signatures of the **foreach()** decorator and the **paramseq**
constructor have been unified.

Testing/documentation-related updates and improvements.

0.1.1 (2014-07-29)
------------------

Minor testing/documentation-related improvements.

0.1.0 (2014-07-29)
------------------

Initial release.
