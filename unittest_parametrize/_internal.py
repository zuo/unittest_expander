import collections
import functools
import inspect
import itertools
import sys
import types

_PY3 = sys.version_info[0] >= 3
_PARAM_SOURCES_ATTR = '__param_item_sources'


## draft example (TODO: remove it)
"""

@parametrize
class MyTest(unittest.TestCase):

    @paramseq
    def my_numbers(cls):
        yield param(1, 2), context(cls.fix, 42)
        yield param(32, 42), context(cls.fix, 42), label('second')
        yield param(721, 523, a=3, b=4).with_context(cls.fix, 42).with_label('third')

    @paramseq
    def my_other_numbers(cls):
        yield 3, 33
        yield 4, 44

    some_numbers = [
        param(
            5, 6, 7,
        ),
        param(
            8, 9, 0,
        )
    ]

    all_my_numbers = my_numbers + my_other_numbers + some_numbers

    @paramseq
    def my_texts(cls):
        yield 'cos tam'
        yield 'czegos tam'

    @expand(my_texts)
    @expand(all_my_numbers)
    def test(self, x, y, text, a=0, b=-1):
        self.assertEqual(foo, x + y)
        self.assertIsInstance(foo, spam)
        self.assertIn(bar, text)
"""



class Context(object):

    def __init__(self, context_manager_factory, *args, **kwargs):
        self._context_manager_factory = context_manager_factory
        self._args = args
        self._kwargs = kwargs

    def _make_context_manager(self):
        return self._context_manager_factory(*self._args, **self._kwargs)


class Label(object):

    def __init__(self, label_text):
        self._label_text = label_text


class Param(object):

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._context_list = []
        self._label_list = []

    def with_context(self, context_manager_factory, *args, **kwargs):
        context = Context(context_manager_factory, *args, **kwargs)
        return self._from_components(
            self._args,
            self._kwargs,
            self._context_list + [context],
            self._label_list)

    def with_label(self, label_text):
        label = Label(label_text)
        return self._from_components(
            self._args,
            self._kwargs,
            self._context_list,
            self._label_list + [label])

    @classmethod
    def _from_param_item(cls, param_item):
        if isinstance(param_item, Param):
            return param_item
        if isinstance(param_item, tuple):
            param_list = [o for o in param_item if isinstance(o, Param)]
            context_list = [o for o in param_item if isinstance(o, Context)]
            label_list = [o for o in param_item if isinstance(o, Label)]
            if not param_list and not context_list and not label_list:
                # just a tuple of values
                # (does not contain any Param/Context/Label instances)
                new = cls(*param_item)
            elif (param_list and
                  len(param_item) == (len(param_list) +
                                      len(context_list) +
                                      len(label_list))):
                # a tuple containing only Param/Context/Label instances
                new = cls._combine_instances(param_list)
                new._context_list.extend(context_list)
                new._label_list.extend(label_list)
            else:
                raise ValueError('wrong param item: {0!r}'.format(param_item))
            return new
        return cls(param_item)

    @classmethod
    def _combine_instances(cls, param_instances):
        args = []
        kwargs = {}
        context_list = []
        label_list = []
        for p in param_instances:
            args.extend(p._args)
            kwargs.update(p._kwargs)
            context_list.extend(p._context_list)
            label_list.append(Label(p._get_label_text()))
        return cls._from_components(args, kwargs, context_list, label_list)

    @classmethod
    def _from_components(cls, args, kwargs, context_list, label_list):
        new = cls(*args, **kwargs)
        new._context_list.extend(context_list)
        new._label_list.extend(label_list)
        return new

    def _get_context_manager_factory(self):
        # NOTE: this method should be called only when
        # self._context_list has already been fully populated
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
                # Py2+Py3-compatibile substitute of exec with a given namespace
                code = compile(src_code, '<string>', 'exec')
                namespace = {'context_list': self._context_list}
                eval(code, namespace)
                self.__cached_cm_factory = namespace['cm_factory']
            else:
                self.__cached_cm_factory = None
            return self.__cached_cm_factory

    def _get_label_text(self):
        if self._label_list:
            return ', '.join(label._label_text for label in self._label_list)
        else:
            sr = self._short_repr
            args_reprs = (sr(val) for val in self._args)
            kwargs_reprs = ('{0}={1}'.format(key, sr(val))
                            for key, val in sorted(self._kwargs.items()))
            return ','.join(itertools.chain(args_reprs, kwargs_reprs))

    @staticmethod
    def _short_repr(obj, max_len=12):
        r = repr(obj)
        if len(r) > max_len:
            r = '<{0}>'.format(r.lstrip('<')[:max_len-2])
        return r


class ParamSeq(object):

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
            self._init_with_param_sources((some_param_source_dict,))
        else:
            self._init_with_param_sources(
                (some_param_source, some_param_source_dict))

    @classmethod
    def _from_param_sources(cls, param_sources):
        self = cls.__new__(cls)
        self._init_with_param_sources(param_sources)
        return self

    def _init_with_param_sources(self, param_sources):
        param_sources = tuple(param_sources)
        for param_src in param_sources:
            if not self._is_instance_of_legal_param_source_class(param_src):
                raise TypeError(
                    'class {0.__class__!r} (of {0!r}) is not a '
                    'legal param source class'.format(param_src))
        self._param_sources = param_sources

    def __add__(self, other):
        if self._is_instance_of_legal_param_source_class(other):
            return self._from_param_sources(self._param_sources + (other,))
        return NotImplemented

    @staticmethod
    def _is_instance_of_legal_param_source_class(obj):
        return isinstance(obj, (
            ParamSeq,
            collections.Sequence,
            collections.Set,
            collections.Mapping,
            collections.Callable)
        ) and not isinstance(obj, (str if _PY3 else basestring))

    def _iter_params(self, test_cls):
        for param_src in self._param_sources:
            if isinstance(param_src, ParamSeq):
                for param in param_src._iter_params(test_cls):
                    yield param
            elif isinstance(param_src, collections.Mapping):
                for label, param_item in param_src.items():
                    yield Param._from_param_item(param_item).with_label(label)
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
                    yield Param._from_param_item(param_item)


# test case *class* decorator...
def parametrize(test_cls):
    all_attrs = vars(test_cls)
    seen_names = set(all_attrs)
    attrs_to_replace_with_counts = dict()
    attrs_to_add = dict()
    for base_name, obj in all_attrs.items():
        param_sources = getattr(obj, _PARAM_SOURCES_ATTR, None)
        if param_sources is not None:
            if not isinstance(obj, types.FunctionType):
                raise TypeError(
                    '{0!r} is not a function and only functions '
                    'can be parametrized'.format(obj))
            base_func = obj
            arg_spec = inspect.getargspec(base_func)
            can_take_context_targets = (
                'context_targets' in arg_spec.args or
                arg_spec.keywords is not None)
            count = 0
            for func in _generate_parametrized_functions(
                    test_cls, param_sources,
                    base_name, base_func, seen_names,
                    can_take_context_targets):
                attrs_to_add[func.__name__] = func
                count += 1
            attrs_to_replace_with_counts[base_name] = count
    for name, count in attrs_to_replace_with_counts.items():
        setattr(test_cls, name, count)
    for name, obj in attrs_to_add.items():
        setattr(test_cls, name, obj)
    return test_cls


# test case *class* decorator...
def _parametrize_expand(*param_sources, **kwargs):
    _into = kwargs.pop('into', None)
    if kwargs:
        raise TypeError(
            'expand_to_suite() got unexpected keyword arguments: ' +
            ', '.join(sorted(map(repr, kwargs))))
    def decorator(base_test_cls):
        into = _resolve_the_into_arg(_into, globals_frame_depth=2)
        seen_names = set(list(into.keys()) + [base_test_cls.__name__])
        count = 0
        parametrize(base_test_cls)
        for cls in _generate_parametrized_classes(
                base_test_cls, param_sources, seen_names):
            into[cls.__name__] = cls
            count += 1
        return count
    return decorator

parametrize.expand = _parametrize_expand


# test case *method* decorator...
def expand(*param_sources):
    def decorator(parametrized_func):
        stored_param_sources = getattr(parametrized_func, _PARAM_SOURCES_ATTR, None)
        if stored_param_sources is None:
            stored_param_sources = []
            setattr(parametrized_func, _PARAM_SOURCES_ATTR, stored_param_sources)
        assert isinstance(stored_param_sources, list)
        stored_param_sources.extend(param_sources)
        return parametrized_func
    return decorator


def _generate_parametrized_functions(test_cls, param_sources,
                                     base_name, base_func, seen_names,
                                     can_take_context_targets):
    for param in _generate_params_from_sources(param_sources, test_cls):
        yield _make_parametrized_func(base_name, base_func, param, seen_names,
                                      can_take_context_targets)


def _generate_parametrized_classes(base_test_cls, param_sources, seen_names):
    for param in _generate_params_from_sources(param_sources, base_test_cls):
        yield _make_parametrized_cls(base_test_cls, param, seen_names)


def _generate_params_from_sources(param_sources, test_cls):
    src_params_iterables = [
        ParamSeq(param_src)._iter_params(test_cls)
        for param_src in param_sources]
    for params_row in itertools.product(*src_params_iterables):
        yield Param._combine_instances(params_row)


def _make_parametrized_func(base_name, base_func, param, seen_names,
                            can_take_context_targets):
    p_args = param._args
    p_kwargs = param._kwargs
    cm_factory = param._get_context_manager_factory()
    if cm_factory is None:
        @functools.wraps(base_func)
        def generated_func(*args, **kwargs):
            args += p_args
            kwargs.update(**p_kwargs)
            if can_take_context_targets:
                kwargs['context_targets'] = []
            return base_func(*args, **kwargs)
    else:
        @functools.wraps(base_func)
        def generated_func(*args, **kwargs):
            args += p_args
            kwargs.update(**p_kwargs)
            with cm_factory() as context_targets:
                if can_take_context_targets:
                    kwargs['context_targets'] = context_targets
                return base_func(*args, **kwargs)
    generated_func.__name__ = _format_name_for_parametrized(
        base_name, param._get_label_text(), seen_names)
    _set_qualname(base_func, generated_func)
    return generated_func


def _make_parametrized_cls(base_test_cls, param, seen_names):
    cm_factory = param._get_context_manager_factory()
    class generated_test_cls(base_test_cls):
        def setUp(self):
            self.params = param._args
            for name, obj in param._kwargs.items():
                setattr(self, name, obj)
            if cm_factory is not None:
                cm = cm_factory()
                cm_type = type(cm)
                if cm_type is cm.__class__:
                    # new-style class
                    cm_exit = cm_type.__exit__
                    cm_enter = cm_type.__enter__
                    self.context_targets = cm_enter(cm)
                    self.addCleanup(cm_exit, cm, None, None, None)
                else:
                    # old-style class (Python 2 only)
                    cm_exit = cm.__exit__
                    cm_enter = cm.__enter__
                    self.context_targets = cm_enter()
                    self.addCleanup(cm_exit, None, None, None)
            return super(generated_test_cls, self).setUp()
    generated_test_cls.__module__ = base_test_cls.__module__
    generated_test_cls.__name__ = _format_name_for_parametrized(
        base_test_cls, param._get_label_text(), seen_names)
    _set_qualname(base_test_cls, generated_test_cls)
    return generated_test_cls


def _format_name_for_parametrized(base_name, label_text, seen_names):
    name = '{0} :: {1}'.format(base_name, label_text)
    if name in seen_names:
        count = 1
        while True:
            # ensuring that, for a particular test class, names are unique
            name_with_count = '{0}__{1}'.format(name, count)
            if name_with_count not in seen_names:
                break
        name = name_with_count
    seen_names.add(name)
    return name


def _set_qualname(base_obj, target_obj):
    # relevant only for Python 3.3+
    qualname = getattr(base_obj, '__qualname__', None)
    if qualname is not None:
        parent_qualname, _ = qualname.rsplit('.', 1)
        target_obj.__qualname__ = '{0}.{1}'.format(
            parent_qualname, target_obj.__name__)


def _resolve_the_into_arg(into, globals_frame_depth):
    orig_into = into
    if into is None:
        into = sys._getframe(globals_frame_depth).f_globals['__name__']
    if isinstance(into, (str if _PY3 else basestring)):
        into = __import__(into, globals(), locals(), ['*'], 0)
    if inspect.ismodule(into):
        into = vars(into)
    if not isinstance(into, collections.MutableMapping):
        raise TypeError(
            "resolved 'into' argument is not a mutable mapping "
            "({!r} given; resolved to {!r})".format(orig_into, into))
    return into
