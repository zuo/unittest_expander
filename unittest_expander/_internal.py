# Copyright (c) 2014 Jan Kaliszewski (zuo). All rights reserved.
# Licensed under MIT License (see the LICENSE.txt file for details).

import collections
import functools
import inspect
import itertools
import string
import sys
import types


_PY3 = sys.version_info[0] >= 3
_CLASS_TYPES = (type,) if _PY3 else (type, types.ClassType)
_STRING_TYPES = (str,) if _PY3 else (str, unicode)

_PARAM_SOURCES_ATTR = '__param_item_sources'

_GENERIC_KWARGS = 'context_targets', 'label'

_DEFAULT_PARAMETRIZED_NAME_PATTERN = '{base_name}__<{label}>'
_DEFAULT_PARAMETRIZED_NAME_FORMATTER = string.Formatter()


class _Context(object):

    def __init__(self, context_manager_factory, *args, **kwargs):
        self._context_manager_factory = context_manager_factory
        self._args = args
        self._kwargs = kwargs

    def _make_context_manager(self):
        return self._context_manager_factory(*self._args, **self._kwargs)


class Substitute(object):

    def __init__(self, actual_object):
        self.actual_object = actual_object

    def __getattribute__(self, name):
        if name in ('actual_object', '__class__', '__call__'):
            return super(Substitute, self).__getattribute__(name)
        return getattr(self.actual_object, name)

    def __dir__(self):
        names = ['actual_object']
        names.extend(
            name
            for name in dir(self.actual_object)
            if name not in ('actual_object', '__call__'))
        return names


class param(object):

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._context_list = []
        self._label_list = []

    def context(self, context_manager_factory, *args, **kwargs):
        context = _Context(context_manager_factory, *args, **kwargs)
        return self._from_components(
            self._args,
            self._kwargs,
            self._context_list + [context],
            self._label_list)

    def label(self, text):
        return self._from_components(
            self._args,
            self._kwargs,
            self._context_list,
            self._label_list + [text])

    @classmethod
    def _from_param_item(cls, param_item):
        if isinstance(param_item, param):
            return param_item
        if isinstance(param_item, tuple):
            return cls(*param_item)
        return cls(param_item)

    @classmethod
    def _combine_instances(cls, param_instances):
        args = []
        kwargs = {}
        context_list = []
        label_list = []
        for param_inst in param_instances:
            args.extend(param_inst._args)
            kwargs.update(param_inst._kwargs)
            context_list.extend(param_inst._context_list)
            label_list.append(param_inst._get_label())
        return cls._from_components(args, kwargs, context_list, label_list)

    @classmethod
    def _from_components(cls, args, kwargs, context_list, label_list):
        new = cls(*args, **kwargs)
        new._context_list.extend(context_list)
        new._label_list.extend(label_list)
        return new

    def _get_context_manager_factory(self):
        try:
            return self.__cached_cm_factory
        except AttributeError:
            if self._context_list:
                # we need to combine several context managers (from the
                # contexts) but Python 2 does not have contextlib.ExitStack
                # and contextlib.nested() is deprecated (for good reasons)
                # -- so we will generate, compile and exec the code:
                src_code = (
                    'import contextlib\n'
                    '@contextlib.contextmanager\n'
                    'def cm_factory():\n'
                    '    context_targets = [None] * len(context_list)\n'
                    '    {0}'
                    'yield context_targets\n'.format(''.join(
                        ('with context_list[{0}]._make_context_manager() '
                         'as context_targets[{0}]:\n{next_indent}'
                        ).format(i, next_indent=((8 + 4 * i) * ' '))
                        for i in range(len(self._context_list)))))
                # Py2+Py3-compatibile substitute of exec in a given namespace
                code = compile(src_code, '<string>', 'exec')
                namespace = {'context_list': self._context_list}
                eval(code, namespace)
                self.__cached_cm_factory = namespace['cm_factory']
            else:
                self.__cached_cm_factory = None
            return self.__cached_cm_factory

    def _get_label(self):
        if self._label_list:
            return ', '.join(label for label in self._label_list)
        else:
            short_repr = self._short_repr
            args_reprs = (short_repr(val) for val in self._args)
            kwargs_reprs = ('{0}={1}'.format(key, short_repr(val))
                            for key, val in sorted(self._kwargs.items()))
            return ','.join(itertools.chain(args_reprs, kwargs_reprs))

    @staticmethod
    def _short_repr(obj, max_len=16):
        r = repr(obj)
        if len(r) > max_len:
            r = '<{0}...>'.format(r.lstrip('<')[:max_len-5])
        return r


class paramseq(object):

    def __init__(*posargs, **some_param_source_dict):
        try:
            self, some_param_source = posargs
        except ValueError:
            try:
                [self] = posargs
            except ValueError:
                raise TypeError(
                    '__init__() takes 1 or 2 positional arguments '
                    '({0} given)'.format(len(posargs)))
            self._init_with_param_sources(some_param_source_dict)
        else:
            if some_param_source_dict:
                raise TypeError(
                    '__init__() can take either positional '
                    'arguments or keyword arguments, not both')
            else:
                self._init_with_param_sources(some_param_source)

    def __add__(self, other):
        if self._is_instance_of_legal_param_source_class(other):
            return self._from_param_sources(self, other)
        return NotImplemented

    def __radd__(self, other):
        if self._is_instance_of_legal_param_source_class(other):
            return self._from_param_sources(other, self)
        return NotImplemented

    def context(self, context_manager_factory, *args, **kwargs):
        context = _Context(context_manager_factory, *args, **kwargs)
        new = self._from_param_sources(self)
        new._context_list.append(context)
        return new

    @classmethod
    def _from_param_sources(cls, *param_sources):
        self = cls.__new__(cls)
        self._init_with_param_sources(*param_sources)
        return self

    def _init_with_param_sources(self, *param_sources):
        param_sources = tuple(param_sources)
        for param_src in param_sources:
            if not self._is_instance_of_legal_param_source_class(param_src):
                raise TypeError(
                    'class {0.__class__!r} (of {0!r}) is not a '
                    'legal parameter source class'.format(param_src))
        self._param_sources = param_sources
        self._context_list = []

    @staticmethod
    def _is_instance_of_legal_param_source_class(obj):
        return isinstance(obj, (
            paramseq,
            collections.Sequence,
            collections.Set,
            collections.Mapping,
            collections.Callable)
        ) and not isinstance(obj, _STRING_TYPES)

    def _generate_params(self, test_cls):
        for param_inst in self._generate_raw_params(test_cls):
            if self._context_list:
                param_inst = param_inst._from_components(
                    param_inst._args,
                    param_inst._kwargs,
                    param_inst._context_list + self._context_list,
                    param_inst._label_list)
            yield param_inst

    def _generate_raw_params(self, test_cls):
        for param_src in self._param_sources:
            if isinstance(param_src, paramseq):
                for param_inst in param_src._generate_params(test_cls):
                    yield param_inst
            elif isinstance(param_src, collections.Mapping):
                for label, param_item in param_src.items():
                    yield param._from_param_item(param_item).label(label)
            else:
                if isinstance(param_src, collections.Callable):
                    try:
                        param_src = param_src(test_cls)
                    except TypeError:
                        param_src = param_src()
                else:
                    assert isinstance(param_src, (collections.Sequence,
                                                  collections.Set))
                for param_item in param_src:
                    yield param._from_param_item(param_item)


# test case *method* or *class* decorator...
def foreach(param_src):
    def decorator(func_or_cls):
        stored_param_sources = getattr(func_or_cls, _PARAM_SOURCES_ATTR, None)
        if stored_param_sources is None:
            stored_param_sources = []
            setattr(func_or_cls, _PARAM_SOURCES_ATTR, stored_param_sources)
        assert isinstance(stored_param_sources, list)
        stored_param_sources.append(param_src)
        return func_or_cls
    return decorator


# test case *class* decorator...
def expand(test_cls=None, **kwargs):
    into = kwargs.pop('into', None)
    if kwargs:
        raise TypeError(
            'expand() got unexpected keyword arguments: ' +
            ', '.join(sorted(map(repr, kwargs))))
    if test_cls is None:
        return functools.partial(expand, into=into)
    _expand_test_methods(test_cls)
    return _expand_test_cls(test_cls, into)


def _expand_test_methods(test_cls):
    attr_names = dir(test_cls)
    seen_names = set(attr_names)
    attrs_to_substitute = dict()
    attrs_to_add = dict()
    for base_name in attr_names:
        obj = getattr(test_cls, base_name, None)
        param_sources = getattr(obj, _PARAM_SOURCES_ATTR, None)
        if param_sources is not None:
            if _PY3:
                # no unbound methods in Python 3
                if not isinstance(obj, types.FunctionType):
                    raise TypeError('{0!r} is not a function'.format(obj))
                base_func = obj
            else:
                if not isinstance(obj, types.MethodType):
                    raise TypeError('{0!r} is not a method'.format(obj))
                base_func = obj.__func__
            arg_spec = inspect.getargspec(base_func)
            accepted_generic_kwargs = set(
                _GENERIC_KWARGS if arg_spec.keywords is not None
                else (kw for kw in _GENERIC_KWARGS
                      if kw in arg_spec.args))
            for func in _generate_parametrized_functions(
                    test_cls, param_sources,
                    base_name, base_func, seen_names,
                    accepted_generic_kwargs):
                attrs_to_add[func.__name__] = func
            attrs_to_substitute[base_name] = obj
    for name, obj in attrs_to_substitute.items():
        setattr(test_cls, name, Substitute(obj))
    for name, obj in attrs_to_add.items():
        setattr(test_cls, name, obj)


def _expand_test_cls(base_test_cls, into):
    param_sources = getattr(base_test_cls, _PARAM_SOURCES_ATTR, None)
    if param_sources is None:
        return base_test_cls
    else:
        if not isinstance(base_test_cls, _CLASS_TYPES):
            raise TypeError('{0!r} is not a class'.format(base_test_cls))
        into = _resolve_the_into_arg(into, globals_frame_depth=3)
        seen_names = set(list(into.keys()) + [base_test_cls.__name__])
        for cls in _generate_parametrized_classes(
                base_test_cls, param_sources, seen_names):
            into[cls.__name__] = cls
        return Substitute(base_test_cls)


def _resolve_the_into_arg(into, globals_frame_depth):
    orig_into = into
    if into is None:
        into = sys._getframe(globals_frame_depth).f_globals['__name__']
    if isinstance(into, _STRING_TYPES):
        into = __import__(into, globals(), locals(), ['*'], 0)
    if inspect.ismodule(into):
        into = vars(into)
    if not isinstance(into, collections.MutableMapping):
        raise TypeError(
            "resolved 'into' argument is not a mutable mapping "
            "({0!r} given, resolved to {1!r})".format(orig_into, into))
    return into


def _generate_parametrized_functions(test_cls, param_sources,
                                     base_name, base_func, seen_names,
                                     accepted_generic_kwargs):
    for count, param_inst in enumerate(
            _generate_params_from_sources(param_sources, test_cls),
            start=1):
        yield _make_parametrized_func(base_name, base_func, count, param_inst,
                                      seen_names, accepted_generic_kwargs)


def _generate_parametrized_classes(base_test_cls, param_sources, seen_names):
    for count, param_inst in enumerate(
            _generate_params_from_sources(param_sources, base_test_cls),
            start=1):
        yield _make_parametrized_cls(base_test_cls, count,
                                     param_inst, seen_names)


def _generate_params_from_sources(param_sources, test_cls):
    src_params_iterables = [
        paramseq(param_src)._generate_params(test_cls)
        for param_src in param_sources]
    for params_row in itertools.product(*src_params_iterables):
        yield param._combine_instances(params_row)


def _make_parametrized_func(base_name, base_func, count, param_inst,
                            seen_names, accepted_generic_kwargs):
    p_args = param_inst._args
    p_kwargs = param_inst._kwargs
    label = param_inst._get_label()
    cm_factory = param_inst._get_context_manager_factory()
    if cm_factory is None:
        @functools.wraps(base_func)
        def generated_func(*args, **kwargs):
            args += p_args
            kwargs.update(**p_kwargs)
            if 'context_targets' in accepted_generic_kwargs:
                kwargs.setdefault('context_targets', [])
            if 'label' in accepted_generic_kwargs:
                kwargs.setdefault('label', label)
            return base_func(*args, **kwargs)
    else:
        @functools.wraps(base_func)
        def generated_func(*args, **kwargs):
            args += p_args
            kwargs.update(**p_kwargs)
            with cm_factory() as context_targets:
                if 'context_targets' in accepted_generic_kwargs:
                    kwargs.setdefault('context_targets', context_targets)
                if 'label' in accepted_generic_kwargs:
                    kwargs.setdefault('label', label)
                return base_func(*args, **kwargs)
    generated_func.__name__ = _format_name_for_parametrized(
        base_name, base_func, label, count, seen_names)
    _set_qualname(base_func, generated_func)
    return generated_func


def _make_parametrized_cls(base_test_cls, count, param_inst, seen_names):
    cm_factory = param_inst._get_context_manager_factory()
    label = param_inst._get_label()

    class generated_test_cls(base_test_cls):

        def setUp(self):
            self.label = label
            self.params = param_inst._args
            for name, obj in param_inst._kwargs.items():
                setattr(self, name, obj)
            exit = None
            try:
                if cm_factory is not None:
                    cm = cm_factory()
                    cm_type = type(cm)
                    if not _PY3 and isinstance(cm_type, types.InstanceType):
                        # old-style class (Python 2 only)
                        cm_exit = cm.__exit__
                        cm_enter = cm.__enter__
                        self.context_targets = cm_enter()
                        exit = cm_exit
                    else:
                        # new-style class
                        cm_type_exit = cm_type.__exit__
                        cm_type_enter = cm_type.__enter__
                        self.context_targets = cm_type_enter(cm)
                        def exit(*exc_info):
                            return cm_type_exit(cm, *exc_info)
                self.__exit = exit
                return super(generated_test_cls, self).setUp()
            except:
                if exit is not None:
                    exc_info = sys.exc_info()
                    try:
                        exit(*exc_info)
                    finally:
                        self.__exit = None
                raise

        def tearDown(self):
            try:
                r = super(generated_test_cls, self).tearDown()
            except:
                exc_info = sys.exc_info()
                exit = self.__exit
                if exit is not None:
                    exit(*exc_info)
                raise
            else:
                exit = self.__exit
                if exit is not None:
                    exit(None, None, None)
                return r
            finally:
                self.__exit = None

    generated_test_cls.__module__ = base_test_cls.__module__
    generated_test_cls.__name__ = _format_name_for_parametrized(
        base_test_cls.__name__, base_test_cls, label, count, seen_names)
    _set_qualname(base_test_cls, generated_test_cls)
    return generated_test_cls


def _format_name_for_parametrized(base_name, base_obj,
                                  label, count, seen_names):
    pattern, formatter = _get_name_pattern_and_formatter()
    name = stem_name = formatter.format(
        pattern,
        base_name=base_name,
        base_obj=base_obj,
        label=label,
        count=count)
    uniq_tag = 2
    while name in seen_names:
        # ensure that, for a particular class, names are unique
        name = '{0}__{1}'.format(stem_name, uniq_tag)
        uniq_tag += 1
    seen_names.add(name)
    return name


def _get_name_pattern_and_formatter():
    pattern = getattr(expand, 'global_name_pattern', None)
    if pattern is None:
        pattern = _DEFAULT_PARAMETRIZED_NAME_PATTERN
    formatter = getattr(expand, 'global_name_formatter', None)
    if formatter is None:
        formatter = _DEFAULT_PARAMETRIZED_NAME_FORMATTER
    return pattern, formatter


def _set_qualname(base_obj, target_obj):
    # relevant to Python 3.3+
    base_qualname = getattr(base_obj, '__qualname__', None)
    if base_qualname is not None:
        base_name = base_obj.__name__
        qualname_prefix = (
            base_qualname[:(len(base_qualname) - len(base_name))]
            if (base_qualname == base_name or
                base_qualname.endswith('.' + base_name))
            else '<...>.')
        target_obj.__qualname__ = qualname_prefix + target_obj.__name__
