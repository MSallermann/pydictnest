import pytest
from collections import defaultdict
from pydictnest import (
    set_nested,
    get_nested,
    has_nested,
    items_nested,
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


def test_unflatten_with_custom_factory_and_overwrite():
    inp = {"m.n": 5, "m.p": 6}
    # use defaultdict for nested dicts
    unflat = unflatten_dict(inp, sep=".", dict_factory=lambda: defaultdict(dict))
    assert isinstance(unflat, defaultdict)
    assert unflat["m"]["n"] == 5
    assert unflat["m"]["p"] == 6


def test_error_on_nonexistent_intermediate_for_has_and_get():
    d = {"u": 1}
    # get_nested should return default if intermediate is not mapping
    assert get_nested(d, ["u", "v"], default=None) is None
    # has_nested should be False
    assert not has_nested(d, ["u", "v"])


if __name__ == "__main__":
    pytest.main()
