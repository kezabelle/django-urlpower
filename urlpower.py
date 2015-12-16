# -*- coding: utf-8 -*-
from __future__ import absolute_import
from collections import OrderedDict, namedtuple
from inspect import Signature, signature
import logging
import sys
from threading import Lock
from django.http import Http404
from django.utils import six
from django.conf import urls as django_urls
import wrapt
from django.utils.module_loading import import_string


logger = logging.getLogger(__name__)


class TypeError404(Http404):
    pass


def to_int(value):
    try:
        return int(value)
    except ValueError:
        raise TypeError404("Could not convert {v!r} to an integer".format(v=value))


def noop(value):
    return value


class apply_named_typecasts(object):
    __slots__ = (
        # 'unnamed_typecasts',
        # 'named_typecasts',
        'converters',
        'signature',
    )

    def __init__(self, signature, unnamed_args, named_args, ignores):
        params = signature.parameters
        bindables = [[k, None] for k, v in params.items()
                     if v.kind == v.POSITIONAL_OR_KEYWORD]

        # remove `request`
        request = ['request', None]
        varself = ['self', None]
        if request in bindables:
            bindables.remove(request)
        if varself in bindables:
            bindables.remove(varself)
        import pdb; pdb.set_trace()
        # replaces None with actual transformers
        # for index, unnamed_arg in enumerate(unnamed_args):
        #     assert callable(unnamed_arg), "Not a callable"
        #     bindables[index][1] = unnamed_arg

        final_args = OrderedDict(bindables)
        # Apply named argument handlers
        for named_arg, named_arg_caster in named_args.items():
            if named_arg in final_args and final_args[named_arg] is None:
                final_args[named_arg] = named_arg_caster
        self.converters = final_args
        self.signature = signature

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        import pdb; pdb.set_trace()
        params = self.signature.bind(*args, **kwargs).arguments
        def convert(k, v):
            converters = self.converters
            if k in converters and callable(converters[k]):
                return converters[k](v)
            return v
        all_args = OrderedDict((k, convert(k,v)) for k, v in params.items())
        # defined = wrapped.__code__.co_argcount
        # unwrap = namedtuple('unwrap', wrapped.__code__.co_varnames[:5])(*args, **kwargs)
        # converters = self.converters
        # all_args = {k: converters[k](v) if k in converters and converters[k] is not None else v
        #             for k, v in unwrap._asdict().items()}
        return wrapped(**all_args)


class UrlPower(object):
    __slots__ = (
        'named_typecasts',
        '_lock',
    )

    def __init__(self, named_typecasts=None):
        self.named_typecasts = {}
        self._lock = Lock()
        if named_typecasts is not None:
            self.register(named_typecasts=named_typecasts)

    def register(self, named_typecasts):
        """
        >>> x = UrlPower()
        >>> def somefunc(value): return 2
        >>> x.register({'test': int, 'custom': somefunc)})
        """
        self._lock.acquire()
        try:
            for k, v in named_typecasts.items():
                if isinstance(v, six.text_type):
                    v = import_string(dotted_path=v)
                self.named_typecasts[k] = v
        finally:
            self._lock.release()

    def include(self, *args, **kwargs):
        original_include = django_urls.include(*args, **kwargs)
        return original_include

    def url(self, regex, view, kwargs=None, name=None, prefix='',
            unnamed_args=None, named_args=None, ignores=()):
        # pass through to normal handler.
        if unnamed_args is None and named_args is None:
            return django_urls.url(regex=regex, view=view, kwargs=kwargs,
                                   name=name, prefix=prefix)
        sig = signature(view)
        view = apply_named_typecasts(signature=sig,
                                     unnamed_args=unnamed_args or (),
                                     named_args=named_args or {},
                                     ignores=ignores)(view)

        original_url = django_urls.url(regex=regex, view=view, kwargs=kwargs,
                                       name=name, prefix=prefix)
        return original_url


urlpower = UrlPower()
include = urlpower.include
url = urlpower.url
