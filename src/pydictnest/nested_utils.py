from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, MutableMapping, Sequence
from typing import Any, TypeVar, cast, overload

__all__ = [
    "flatten_dict",
    "get_nested",
    "has_nested",
    "items_nested",
    "keys_nested",
    "set_nested",
    "unflatten_dict",
    "values_nested",
]

# The input and output mapping types are deliberately independent. These helpers
# only read the input, while ``dict_factory`` determines the concrete mutable
# mapping type they create and return.
_OutputMappingT = TypeVar("_OutputMappingT", bound=MutableMapping[str, Any])


def _require_keys(keys: Sequence[str]) -> None:
    if not keys:
        msg = "keys must contain at least one key"
        raise ValueError(msg)


def set_nested(
    dictionary: MutableMapping[str, Any],
    keys: Sequence[str],
    value: Any,
    subdict_factory: Callable[[], MutableMapping[str, Any]] = dict,
) -> None:
    """Set a value in a nested dictionary structure, creating intermediate dictionaries as needed.

    Args:
        dictionary (MutableMapping): The dictionary to modify.
        keys (Sequence[str]): A sequence of keys specifying the nested path.
        value (Any): The value to set at the nested location.
        subdict_factory (Callable, optional): A factory function to create new sub-dictionaries.
            Defaults to dict.

    Returns:
        None

    Raises:
        ValueError: If ``keys`` is empty.

    Example:
        >>> d = {}
        >>> set_nested(d, ["a", "b", "c"], 1)
        >>> print(d)
        {'a': {'b': {'c': 1}}}

    """
    _require_keys(keys)

    if len(keys) == 1:
        dictionary[keys[0]] = value
    else:
        first_key = keys[0]
        subdict = dictionary.get(first_key)
        if not isinstance(subdict, MutableMapping):
            subdict = subdict_factory()
            dictionary[first_key] = subdict
        set_nested(
            dictionary=cast("MutableMapping[str, Any]", subdict),
            keys=keys[1:],
            value=value,
            subdict_factory=subdict_factory,
        )


def has_nested(dictionary: Mapping[str, Any], keys: Sequence[str]) -> bool:
    """Determine whether a nested key path exists in a dictionary.

    Args:
        dictionary (Mapping): The mapping to inspect.
        keys (Sequence[str]): A sequence of keys specifying the nested path.

    Returns:
        bool: True if the full key path exists, False otherwise.

    Raises:
        ValueError: If ``keys`` is empty.

    Example:
        >>> d = {"a": {"b": 2}}
        >>> has_nested(d, ["a", "b"])
        True
        >>> has_nested(d, ["a", "c"])
        False

    """
    _require_keys(keys)

    if len(keys) == 1:
        return keys[0] in dictionary
    first_key = keys[0]
    subdict = dictionary.get(first_key)
    if not isinstance(subdict, Mapping):
        return False
    return has_nested(
        dictionary=cast("Mapping[str, Any]", subdict),
        keys=keys[1:],
    )


def get_nested(
    dictionary: Mapping[str, Any],
    keys: Sequence[str],
    default: Any = None,
) -> Any:
    """Retrieve a value from a nested dictionary, returning a default if any key is missing.

    Args:
        dictionary (Mapping): The mapping to query.
        keys (Sequence[str]): A sequence of keys specifying the nested path.
        default (Any, optional): The value to return if the path is not found. Defaults to None.

    Returns:
        Any: The value at the nested location, or default if not present.

    Raises:
        ValueError: If ``keys`` is empty.

    Example:
        >>> d = {"a": {"b": 3}}
        >>> get_nested(d, ["a", "b"])
        3
        >>> get_nested(d, ["a", "c"], default=0)
        0

    """
    _require_keys(keys)

    if len(keys) == 1:
        return dictionary.get(keys[0], default)
    first_key = keys[0]
    if first_key not in dictionary:
        return default
    subdict = dictionary[first_key]

    if not isinstance(subdict, Mapping):
        return default

    # We assume any mapping has `str` as keys, but we do not explicitly check this
    # hence the cast(...)
    return get_nested(
        dictionary=cast("Mapping[str, Any]", subdict),
        keys=keys[1:],
        default=default,
    )


def items_nested(
    d: Mapping[str, Any],
    subkeys: Sequence[str] | None = None,
) -> Iterator[tuple[list[str], Any]]:
    """Yield all key paths and corresponding values in a nested dictionary in depth-first order.

    Args:
        d (Mapping): The mapping to iterate.
        subkeys (Sequence[str], optional): Intermediate key path during recursion. Defaults to [].

    Yields:
        Iterator[tuple[list[str], Any]]: Tuples of ``(key_path, value)`` for
            each leaf node.

    Example:
        >>> inp = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}
        >>> list(items_nested(inp))
        [(['a', 'b'], 1), (['a', 'c', 'd'], 2), (['e'], 3)]

    """
    if subkeys is None:
        subkeys = []

    for key, value in d.items():
        current_path = [*list(subkeys), key]
        if isinstance(value, Mapping):
            # We assume any mapping has `str` as keys, but we do not explicitly check this
            # hence the cast(...)
            yield from items_nested(
                cast("Mapping[str, Any]", value), subkeys=current_path
            )
        else:
            yield current_path, value


def keys_nested(d: Mapping[str, Any]) -> Iterator[list[str]]:
    """Yield all key paths in a nested dictionary in depth-first order."""
    for k, _ in items_nested(d):
        yield k


def values_nested(d: Mapping[str, Any]) -> Iterator[Any]:
    """Yield all values in a nested dictionary in depth-first order."""
    for _, v in items_nested(d):
        yield v


# A type checker cannot infer ``_OutputMappingT`` from the runtime default
# ``dict`` when ``dict_factory`` is omitted. This overload explicitly describes
# that common case so callers receive ``dict[str, Any]`` rather than an unknown
# or generic mutable-mapping type.
@overload
def flatten_dict(
    dictionary: Mapping[str, object],
    sep: str = ".",
) -> dict[str, Any]: ...


# Preserve the exact factory result for the original positional calling form:
# ``flatten_dict(mapping, separator, factory)``.
@overload
def flatten_dict(
    dictionary: Mapping[str, object],
    sep: str,
    dict_factory: Callable[[], _OutputMappingT],
) -> _OutputMappingT: ...


# This separate form allows callers to omit ``sep`` and supply only a keyword
# factory: ``flatten_dict(mapping, dict_factory=factory)``. Python cannot put a
# required positional parameter after the defaulted ``sep`` parameter.
@overload
def flatten_dict(
    dictionary: Mapping[str, object],
    *,
    sep: str = ".",
    dict_factory: Callable[[], _OutputMappingT],
) -> _OutputMappingT: ...


def flatten_dict(
    dictionary: Mapping[str, object],
    sep: str = ".",
    dict_factory: Callable[[], MutableMapping[str, Any]] = dict,
) -> MutableMapping[str, Any]:
    """Flatten a nested dictionary into a single-level dict with concatenated keys.

    Args:
        dictionary (Mapping): The nested mapping to flatten.
        sep (str, optional): Separator between keys. Defaults to '.'.
        dict_factory (Callable, optional): Factory for the output dictionary. Defaults to dict.

    Returns:
        MutableMapping: A new flattened dictionary.

    Example:
        >>> inp = {"a": {"b": 1, "c": {"d": 2}}, "e": 3}
        >>> flatten_dict(inp, sep=":")
        {'a:b': 1, 'a:c:d': 2, 'e': 3}

    """
    result = dict_factory()
    for path, value in items_nested(dictionary):
        flat_key = sep.join(path)
        result[flat_key] = value
    return result


# ``unflatten_dict`` follows the same rules: the default factory returns a
# regular dict, while a supplied factory controls the precise return type.
@overload
def unflatten_dict(
    dictionary: Mapping[str, object],
    sep: str = ".",
) -> dict[str, Any]: ...


# Retain support for a positional separator and factory.
@overload
def unflatten_dict(
    dictionary: Mapping[str, object],
    sep: str,
    dict_factory: Callable[[], _OutputMappingT],
) -> _OutputMappingT: ...


# Also support omitting ``sep`` when the custom factory is passed by keyword.
@overload
def unflatten_dict(
    dictionary: Mapping[str, object],
    *,
    sep: str = ".",
    dict_factory: Callable[[], _OutputMappingT],
) -> _OutputMappingT: ...


def unflatten_dict(
    dictionary: Mapping[str, object],
    sep: str = ".",
    dict_factory: Callable[[], MutableMapping[str, Any]] = dict,
) -> MutableMapping[str, Any]:
    """Reconstruct a nested dictionary from a flattened dictionary.

    Args:
        dictionary (Mapping): Flat mapping with joined keys.
        sep (str, optional): Separator used in flat keys. Defaults to '.'.
        dict_factory (Callable, optional): Factory for intermediate dictionaries. Defaults to dict.

    Returns:
        MutableMapping: A new nested mapping produced by ``dict_factory``.

    Example:
        >>> inp = {"a.b": 1, "a.c.d": 2, "e": 3}
        >>> unflatten_dict(inp, sep=".")
        {'a': {'b': 1, 'c': {'d': 2}}, 'e': 3}

    """
    result = dict_factory()
    for flat_key, value in dictionary.items():
        keys = flat_key.split(sep)
        set_nested(result, keys, value, subdict_factory=dict_factory)
    return result
