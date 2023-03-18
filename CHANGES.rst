Changes
=======

0.4.2 (2023-03-18)
------------------

* A minor interface usability fix: from now on, the **expand()**
  decorator's attributes **global_name_pattern** and
  **global_name_formatter** are both initially set to **None**
  (previously, by default, they were not initialized at all, so
  trying to get any of them without first setting it caused an
  **AttributeError**).

* Documentation: several updates, improvements and minor fixes.


0.4.1 (2023-03-17)
------------------

* Added to the **unittest_expander** module the **__version__** constant.

* Improvements and additions related to tests, CI, generation of
  documentation, etc.; in particular: added a script that checks whether
  **unittest_expander.__version__** is equal to **version** in package
  metadata, and added invocation of that script to the *Install and
  Test* GitHub workflow.

* Documentation: improvements and minor fixes.


0.4.0 (2023-03-16)
------------------

* From now on, the following versions of Python *are officially
  supported:* **3.11**, **3.10**, **3.9**, **3.8**, **3.7**, **3.6**
  and **2.7** (still).  This means, in particular, that the versions
  *3.5*, *3.4*, *3.3*, *3.2* and *2.6* are *no longer supported*.

* Now, if two (or more) parameter collections are combined to make the
  Cartesian product of them (as an effect of decorating a test with
  two or more **foreach(...)** invocations), and a conflict is detected
  between any *keyword arguments* passed earlier to the **param()**
  constructor to create the **param** instances that are being combined,
  the **expand()** decorator raises a **ValueError** (in older versions
  of *unittest_expander* no exception was raised; instead, a keyword
  argument being a component of one **param** was silently overwritten
  by the corresponding keyword argument being a component of the other
  **param**; that could lead to silent bugs in your tests...).

* When it comes to **param.context()** (and **paramseq.context()**),
  now the standard Python context manager's mechanism of suppressing
  exceptions (by making **__exit__()** return a *true* value) is,
  by default, consistently *disabled* (i.e. exceptions are *not*
  suppressed, as it could easily become a cause of silent test bugs; the
  previous behavior was inconsistent: exceptions could be suppressed in
  the case of applying **foreach()** decorators to test *methods*, but
  not in the case of applying them to test *classes*).

  If needed, the possibility of suppressing exceptions by **__exit__()**
  returning a *true* value can be explicitly *enabled* on a case-by-case
  basis by passing ``_enable_exc_suppress_=True`` to **param.context()**
  (or **paramseq.context()**).

* **Deprecation notice:** decorating test *classes* with **foreach()**
  -- to generate new parametrized test *classes* -- is now deprecated
  (causing emission of a **DeprecationWarning**); in future versions of
  *unittest_expander* it will first become **unsupported** (in *0.5.0*),
  and then, in some version, will (most probably) get a **new meaning**.
  The current shape of the feature is deemed broken by design (in
  particular, because of the lack of composability; that becomes
  apparent when class inheritance comes into play...).

* **Deprecation notice:** a change related to the deprecation described
  above is that now the **expand()**'s keyword argument ``into`` is also
  deprecated (its use causes emission of a **DeprecationWarning**) and
  will become **illegal** in *unittest_expander 0.5.0*.

* **Deprecation notice:** using a tuple (i.e., an instance of the
  built-in type **tuple** or of any subclass of it, e.g., a *named
  tuple*) as a *parameter collection* -- passed as the *sole* argument
  to **foreach()** or **paramseq()**, or added (using ``+``) to an
  existing **paramseq** object -- is now deprecated (causing emission
  of a **DeprecationWarning**) and will become **illegal** in
  *unittest_expander 0.5.0*.  Instead of a tuple, use a collection
  of another type (e.g., a **list**).

  Note: this deprecation concerns tuples used as *parameter collections*,
  *not* as *items* of parameter collections (tuples being such items,
  acting as simple substitutes of **param** objects, are -- and will
  always be -- perfectly OK).

* Two compatibility fixes:

  (1) now test methods with *keyword-only* arguments and/or *type
  annotations* are supported (previously an error was raised by
  **expand()** if such a method was decorated with **foreach()**);
  the background is that under Python 3.x, from now on,
  **inspect.getfullargspec()** (instead of its legacy predecessor,
  **inspect.getargspec()**) is used to inspect test method signatures;

  (2) now standard *abstract base classes* of collections are imported
  from ``collections.abc``; an import from ``collections`` is left only
  as a Python-2.7-dedicated fallback.

* Two bugfixes related to the **expand()** decorator:

  (1) now class/type objects and **Substitute** objects are ignored
  when scanning a test class for attributes (methods) that have
  **foreach()**-created marks;

  (2) **foreach()**-created marks are no longer retained on parametrized
  test methods generated by the **expand()**'s machinery.

  Thanks to those fixes, it is now possible to apply **expand()** to
  subclasses of an **expand()**-ed class -- provided that **foreach()**
  has been applied only to test *methods* (not to test *classes*, which
  is a deprecated feature anyway -- see the relevant *deprecation
  notice* above).

* A few bugfixes related to applying **foreach()** to test classes
  (which is a deprecated feature -- see the relevant *deprecation
  notice* above):

  (1) a **foreach()**-decorated test class which does *not* inherit
  from **unittest.TestCase** is no longer required to provide its
  own implementations of **setUp()** and **tearDown()** (previously,
  if they were missing, an **AttributeError** were raised by the
  **setUp()** and **tearDown()** implementations provided by
  **expand()**-generated subclasses);

  (2) now the ``context_targets`` attribute of a test class instance
  is set also if there are no contexts (to an empty list -- making it
  possible for a test code to refer to ``self.context_targets`` without
  fear of an **AttributeError**);

  (3) now a *context*'s **__exit__()** is never called without the
  corresponding **__enter__()** call being successful.

* A few really minor behavioral changes/improvements (in particular, now
  a *callable* parameter collection is required to satisfy the built-in
  **callable(...)** predicate, instead of the previously checked
  **isinstance(..., collections.Callable)** condition; that should not
  matter in practice).

* A bunch of package-setup-and-metadata-related additions, updates,
  fixes, improvements and removals (in particular, ``pyproject.toml``
  and ``setup.cfg`` files have been added, and the ``setup.py`` file has
  been removed).

* Added ``.gitignore`` and ``.editorconfig`` files.

* A bunch of changes related to tests, CI, documentation, etc.:
  updates, fixes, improvements and additions (including addition
  of the *Install and Test* GitHub workflow).

**Many thanks** to:

* KOLANICH (`@KOLANICH <https://github.com/KOLANICH>`_),
* Hugo van Kemenade (`@hugovk <https://github.com/hugovk>`_),
* John Vandenberg (`@jayvdb <https://github.com/jayvdb>`_)

-- for their invaluable contribution to this release!


0.3.1 (2014-08-19)
------------------

* Several tests/documentation-related fixes and improvements.


0.3.0 (2014-08-17)
------------------

* Improved signatures of the **foreach()** decorator and the
  **paramseq()** constructor: they take either exactly one positional
  argument which must be a test parameter collection (as previously: a
  sequence/mapping/set or a **paramseq** instance, or a callable
  returning an iterable...), or *any number of positional and/or keyword
  arguments* being test parameters (singular parameter values, tuples of
  parameter values or **param** instances...).  For example,
  ``@foreach([1, 42])`` can now also be spelled as ``@foreach(1, 42)``.

* Several tests/documentation-related updates, fixes and improvements.


0.2.1 (2014-08-12)
------------------

* Important setup/configuration fixes (repairing 0.2.0 regressions):

  * a setup-breaking bug in *setup.py* has been fixed;
  * a bug in the configuration of Sphinx (the tool used to generate
    the documentation) has been fixed.

* Some setup-related cleanups.


0.2.0 (2014-08-11)
------------------

* Now **unittest_expander** is a one-file module, not a directory-based
  package.

* Some documentation improvements and updates.

* Some library setup improvements and refactorings.


0.1.2 (2014-08-01)
------------------

* The signatures of the **foreach()** decorator and the **paramseq()**
  constructor have been unified.

* Tests/documentation-related updates and improvements.


0.1.1 (2014-07-29)
------------------

* Minor tests/documentation-related improvements.


0.1.0 (2014-07-29)
------------------

* Initial release.
