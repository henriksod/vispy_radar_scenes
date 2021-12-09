#!/usr/bin/env python
# Useful when combined with: http://pythoncentral.io/validate-python-function-parameters-and-return-types-with-decorators/

class Maybe(type):
    ''' Metaclass to match types with optionally none.  Use maybe() instead '''
    maybe_type = type(None)  # Overridden in derived classes

    def __instancecheck__(self, instance):
        return isinstance(instance, self.maybe_type) or instance is None

    def __repr__(self):
        return "<class Maybe({})>".format(self.maybe_type)


def maybe(arg_type):
    '''
    Helper for @accepts and @returns decorator.  Maybe means optionally None.
    Example:
        @accepts(maybe(int), str, maybe(dict))
        def foo(a, b, c):
            # a - can be int or None
            # b - must be str
            # c - can be dict or None
    See: https://wiki.haskell.org/Maybe
    '''

    class Derived(metaclass=Maybe):
        maybe_type = arg_type

    return Derived


assert isinstance(42, maybe(int))
assert isinstance(None, maybe(int))
assert not isinstance('1', maybe(int))
# TODO: currently: maybe(int) != maybe(int), so some more specialized equiment is needed for equality checking.