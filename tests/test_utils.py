import pytest
from _pytest.outcomes import Failed
from attr import attrib, attrs
from pytest import raises

from pytest_bdd.utils import deepattrgetter, doesnt_raise, setdefaultattr


def test_get_attribute():
    @attrs
    class Foo:
        foo = attrib()

    item = Foo(foo=1)

    assert deepattrgetter("foo")(item) == (1,)


def test_get_multi_attribute():
    @attrs
    class Foo:
        foo = attrib()
        boo = attrib()

    item = Foo(foo=1, boo=2)

    assert deepattrgetter("boo", "foo")(item) == (2, 1)


def test_get_default_for_attribute():
    class Foo:
        ...

    item = Foo()

    assert deepattrgetter("foo", default=1)(item) == (1,)


def test_get_default_for_multi_attribute():
    class Foo:
        ...

    item = Foo()

    assert deepattrgetter("boo", "foo", default=1)(item) == (1, 1)


def test_raise_on_missing_attribute():
    class Foo:
        ...

    item = Foo()

    with raises(AttributeError):
        deepattrgetter("foo")(item)


def test_raise_on_missing_multi_attribute():
    class Foo:
        ...

    item = Foo()

    with raises(AttributeError):
        deepattrgetter("foo", "boo")(item)


def test_raise_on_missing_nested_attribute():
    class Foo:
        ...

    item = Foo()

    with raises(AttributeError):
        deepattrgetter("foo.bar")(item)


def test_raise_on_missing_multi_nested_attribute():
    class Foo:
        ...

    item = Foo()

    with raises(AttributeError):
        deepattrgetter("foo.bar", "boo.car")(item)


def test_get_nested_attribute():
    @attrs
    class Foo:
        foo = attrib()

    @attrs
    class Bar:
        bar = attrib()

    item = Foo(foo=Bar(bar=1))

    assert deepattrgetter("foo.bar")(item) == (1,)


def test_get_nested_multi_attribute():
    @attrs
    class Foo:
        foo = attrib()
        boo = attrib()

    @attrs
    class Bar:
        bar = attrib()

    @attrs
    class Boo:
        boo = attrib()

    item = Foo(foo=Bar(bar=1), boo=Boo(2))

    assert deepattrgetter("boo.boo", "foo.bar")(item) == (2, 1)


def test_skip_missing_attributes():
    @attrs
    class Foo:
        foo = attrib()
        boo = attrib()

    item = Foo(foo="bar", boo="baz")

    assert deepattrgetter("foo", "boo", "missing", skip_missing=True)(item) == ("bar", "baz")


def test_skip_missing_attributes_nested():
    @attrs
    class Foo:
        foo = attrib()
        boo = attrib()

    @attrs
    class Bar:
        bar = attrib()

    @attrs
    class Boo:
        boo = attrib()

    item = Foo(foo=Bar(bar=1), boo=Boo(2))

    assert deepattrgetter("boo.boo", "foo.bar", "missing.missing", skip_missing=True)(item) == (2, 1)


def test_skip_missing_and_default_attributes():
    @attrs
    class Foo:
        foo = attrib()
        boo = attrib()

    item = Foo(foo="bar", boo="baz")

    with raises(ValueError):
        deepattrgetter("foo", "boo", "missing", skip_missing=True, default=object())(item)


def test_setdefaultattr_set_nonexisting_attr_value():
    class Dumb:
        ...

    dumb = Dumb()
    setdefaultattr(dumb, "foo", value=10)

    assert dumb.foo == 10


def test_setdefaultattr_set_nonexisting_attr_value_factory():
    class Dumb:
        ...

    dumb = Dumb()
    setdefaultattr(dumb, "foo", value_factory=lambda: 10)

    assert dumb.foo == 10


def test_setdefaultattr_not_set_existing_attr_value():
    class Dumb:
        ...

    dumb = Dumb()
    dumb.foo = 20
    setdefaultattr(dumb, "foo", value=10)

    assert dumb.foo == 20


def test_setdefaultattr_not_set_existing_attr_value_factory():
    class Dumb:
        ...

    dumb = Dumb()
    dumb.foo = 20
    setdefaultattr(dumb, "foo", value_factory=lambda: 10)

    assert dumb.foo == 20


def test_setdefaultattr_for_both_factory_and_value():
    class Dumb:
        ...

    with pytest.raises(ValueError):
        setdefaultattr(Dumb(), "a", value=10, value_factory=lambda: 20)


def test_doesnt_raise_fails_test():
    with raises(Failed):
        with doesnt_raise(RuntimeError):
            raise RuntimeError


def test_doesnt_raise_suppress_if_not_match():
    try:
        with doesnt_raise(RuntimeError, match="cool"):
            raise RuntimeError("nice")
    except Exception as e:  # pragma: no cover
        raise AssertionError from e


def test_doesnt_raise_not_suppress_if_not_match_explicitly():
    with raises(RuntimeError, match="nice"):
        with doesnt_raise(RuntimeError, match="cool", suppress_not_matched=False):
            raise RuntimeError("nice")


def test_doesnt_raise_passes_original_exception_if_not_suppressed():
    with raises(ValueError):
        with doesnt_raise(RuntimeError, suppress_not_matched=False):
            raise ValueError("nice")
