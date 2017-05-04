# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import inspect
from django.conf.urls import url

class APISpec(object):
    """
    A collection of functions grouped under a version string.
    Any method in the class that does not start with an `_` is
    considered an APISpec method.
    All APISpec methods must accept "request" as their first parameter.
    e.g.
    def add(self, request, a, b):
        return a + b
    """

    def __init__(self, version):
        assert isinstance(version, basestring)
        self.version = version

    def __unicode__(self):
        return "<APISpec: %s version: %s>" % (self.__class__.__name__, self.version)

    __str__ = __unicode__

class API(object):
    """
    A collection of APISpec's

    api = API(spec1, spec2, spec3)

    # in urls.py, include them as
    url(r'^api/', include(api.urls))
    """

    def __init__(self, *api_specs):
        self.urls = []

        ver_to_fn_map = {}
        for spec in api_specs:
            version = spec.version

            fn_name_to_fn = ver_to_fn_map.setdefault(version, {})
            for fn_name, fn in self._get_api_spec_methods(spec):
                fn_name_to_fn[fn_name] = fn

                pattern = r'^{version}/{fn_name}/?$'.format(
                    version=version, fn_name=fn_name,
                )
                self.urls.append(url(pattern, fn))

        self.ver_to_fn_map = ver_to_fn_map

    def _get_api_spec_methods(self, spec):
        members = inspect.getmembers(spec, predicate=inspect.ismethod)
        for fn_name, fn in members:
            if fn_name.startswith('_'):
                continue

            yield (fn_name, fn)
