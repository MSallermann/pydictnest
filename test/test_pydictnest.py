import pytest
from collections import defaultdict
from types import MappingProxyType
from pydictnest import (
    set_nested,
    get_nested,
    has_nested,
    items_nested,
    keys_nested,
    values_nested,
    flatten_dict,
    unflatten_dict,
)


def test_set_and_get_nested_simple():
    d = {}
    # set a simple nested value
    set_nested(d, ["x", "y", "z"], 42)
    assert d == {"x": {"y": {"z": 42}}}
    # retrieve it
    assert get_nested(d, ["x", "y", "z"]) == 42
    assert get_nested(d, ["x", "a", "b"], default="missing") == "missing"
    assert has_nested(d, ["x", "y", "z"])
    assert not has_nested(d, ["x", "y", "q"])


def test_set_overwrites_non_mapping_intermediate():
    d = {"a": 1}
    # existing non-mapping intermediate should be replaced by dict
    set_nested(d, ["a", "b"], 100)
    assert isinstance(d["a"], dict)
    assert d["a"]["b"] == 100


def test_iterate_nested_dict_and_round_trip():
    inp = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}
    seen = {}
    for path, value in items_nested(inp):
        # reconstruct value via get_nested
        assert get_nested(inp, path) == value
        # test set_nested assigns correctly
        set_nested(inp, path, 999)
        seen[tuple(path)] = True
    # ensure all leaf paths were visited and updated
    for path in seen:
        assert get_nested(inp, list(path)) == 999


def test_flatten_and_unflatten_round_trip():
    inp = {"a": {"b": 1.0, "c": 2.0, "d": {"e": "test"}}, "f": [1, 2]}
    flat = flatten_dict(inp, sep=".")
    expected_flat = {"a.b": 1.0, "a.c": 2.0, "a.d.e": "test", "f": [1, 2]}
    assert flat == expected_flat
    # round-trip
    unflat = unflatten_dict(flat, sep=".")
    assert unflat == inp


def test_flatten_with_custom_dict_factory():
    inp = {"x": {"y": 10}}
    # use defaultdict as output
    flat = flatten_dict(inp, sep="-", dict_factory=lambda: defaultdict(dict))
    assert isinstance(flat, defaultdict)
    assert flat["x-y"] == 10


@pytest.mark.parametrize(
    "source",
    [{"a.b": 1}, {"a": {"b.c": 1}}, {"a.b": {}}],
)
def test_flatten_rejects_keys_containing_separator(source):
    with pytest.raises(ValueError, match="contains separator"):
        flatten_dict(source)


def test_unflatten_with_custom_factory_and_overwrite():
    inp = {"m.n": 5, "m.p": 6}
    # use defaultdict for nested dicts
    unflat = unflatten_dict(inp, sep=".", dict_factory=lambda: defaultdict(dict))
    assert isinstance(unflat, defaultdict)
    assert unflat["m"]["n"] == 5
    assert unflat["m"]["p"] == 6


@pytest.mark.parametrize(
    "source",
    [
        {"a": 1, "a.b": 2},
        {"a.b": 2, "a": 1},
        {"a.b.c": 3, "a.b": 2},
    ],
)
def test_unflatten_rejects_conflicting_paths(source):
    with pytest.raises(ValueError, match="both a value and a parent"):
        unflatten_dict(source)


@pytest.mark.parametrize("function", [flatten_dict, unflatten_dict])
def test_flatten_functions_reject_empty_separator(function):
    with pytest.raises(ValueError, match="sep must not be empty"):
        function({"a": 1}, sep="")


def test_error_on_nonexistent_intermediate_for_has_and_get():
    d = {"u": 1}
    # get_nested should return default if intermediate is not mapping
    assert get_nested(d, ["u", "v"], default=None) is None
    # has_nested should be False
    assert not has_nested(d, ["u", "v"])


def test_keys_and_values():
    inp = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}

    keys = list(keys_nested(inp))
    values = list(values_nested(inp))
    items = list(items_nested(inp))

    assert list(zip(keys, values)) == items


def test_read_only_mappings():
    nested = MappingProxyType(
        {
            "a": MappingProxyType({"b": 1, "c": MappingProxyType({"d": 2})}),
            "e": 3,
        }
    )

    assert has_nested(nested, ["a", "c", "d"])
    assert get_nested(nested, ["a", "b"]) == 1
    assert list(items_nested(nested)) == [
        (["a", "b"], 1),
        (["a", "c", "d"], 2),
        (["e"], 3),
    ]
    assert list(keys_nested(nested)) == [["a", "b"], ["a", "c", "d"], ["e"]]
    assert list(values_nested(nested)) == [1, 2, 3]
    assert flatten_dict(nested) == {"a.b": 1, "a.c.d": 2, "e": 3}

    flat = MappingProxyType({"a.b": 1, "a.c.d": 2, "e": 3})
    assert unflatten_dict(flat) == {"a": {"b": 1, "c": {"d": 2}}, "e": 3}


@pytest.mark.parametrize("function", [set_nested, has_nested, get_nested])
def test_empty_key_path_raises_value_error(function):
    with pytest.raises(ValueError, match="at least one key"):
        if function is set_nested:
            function({}, [], 1)
        else:
            function({}, [])


def test_get_nested_returns_mapping_default_without_traversing_it():
    default = {"child": "not a nested result"}

    assert get_nested({}, ["missing", "child"], default=default) is default


if __name__ == "__main__":
    pytest.main()
