from collections.abc import MutableMapping, Sequence, Callable
from typing import Any, Union, Iterator, Tuple


def set_nested(
    dictionary: MutableMapping,
    keys: Sequence[str],
    value: Any,
    subdict_factory: Callable = dict,
) -> None:
    """
    Set a value in a nested dictionary structure, creating intermediate dictionaries as needed.

    Args:
        dictionary (MutableMapping): The dictionary to modify.
        keys (Sequence[str]): A sequence of keys specifying the nested path.
        value (Any): The value to set at the nested location.
        subdict_factory (Callable, optional): A factory function to create new sub-dictionaries.
            Defaults to dict.

    Returns:
        None

    Example:
        >>> d = {}
        >>> set_nested(d, ['a', 'b', 'c'], 1)
        >>> print(d)
        {'a': {'b': {'c': 1}}}
    """
    if len(keys) <= 1:
        dictionary[keys[0]] = value
    else:
        first_key = keys[0]
        if first_key not in dictionary or not isinstance(
            dictionary[first_key], MutableMapping
        ):
            dictionary[first_key] = subdict_factory()
        set_nested(
            dictionary=dictionary[first_key],
            keys=keys[1:],
            value=value,
            subdict_factory=subdict_factory,
        )


def has_nested(dictionary: MutableMapping, keys: Sequence[str]) -> bool:
    """
    Determine whether a nested key path exists in a dictionary.

    Args:
        dictionary (MutableMapping): The dictionary to inspect.
        keys (Sequence[str]): A sequence of keys specifying the nested path.

    Returns:
        bool: True if the full key path exists, False otherwise.

    Example:
        >>> d = {'a': {'b': 2}}
        >>> has_nested(d, ['a', 'b'])
        True
        >>> has_nested(d, ['a', 'c'])
        False
    """
    if len(keys) <= 1:
        return keys[0] in dictionary
    first_key = keys[0]
    if first_key not in dictionary or not isinstance(
        dictionary[first_key], MutableMapping
    ):
        return False
    return has_nested(dictionary=dictionary[first_key], keys=keys[1:])


def get_nested(
    dictionary: MutableMapping, keys: Sequence[str], default: Any = None
) -> Any:
    """
    Retrieve a value from a nested dictionary, returning a default if any key is missing.

    Args:
        dictionary (MutableMapping): The dictionary to query.
        keys (Sequence[str]): A sequence of keys specifying the nested path.
        default (Any, optional): The value to return if the path is not found. Defaults to None.

    Returns:
        Any: The value at the nested location, or default if not present.

    Example:
        >>> d = {'a': {'b': 3}}
        >>> get_nested(d, ['a', 'b'])
        3
        >>> get_nested(d, ['a', 'c'], default=0)
        0
    """
    if len(keys) <= 1:
        return dictionary.get(keys[0], default)
    first_key = keys[0]
    subdict = dictionary.get(first_key, default)
    if not isinstance(subdict, MutableMapping):
        return default
    return get_nested(dictionary=subdict, keys=keys[1:], default=default)


def items_nested(
    d: MutableMapping, subkeys: Sequence[str] = []
) -> Iterator[Tuple[Sequence[str], Any]]:
    """
    Yield all key paths and corresponding values in a nested dictionary in depth-first order.

    Args:
        d (MutableMapping): The dictionary to iterate.
        subkeys (Sequence[str], optional): Intermediate key path during recursion. Defaults to [].

    Yields:
        Iterator[Tuple[Sequence[str], Any]]: Tuples of (key_path, value) for each leaf node.

    Example:
        >>> inp = {'a': {'b': 1, 'c': {'d': 2}}, 'e': 3}
        >>> list(items_nested(inp))
        [(['a', 'b'], 1), (['a', 'c', 'd'], 2), (['e'], 3)]
    """
    for key, value in d.items():
        current_path = subkeys + [key]
        if isinstance(value, MutableMapping):
            yield from items_nested(value, subkeys=current_path)
        else:
            yield current_path, value


def keys_nested(d: MutableMapping) -> Iterator[Sequence[str]]:
    """Yield all key paths in a nested dictionary in depth-first order."""
    for k, _ in items_nested(d):
        yield k


def values_nested(d: MutableMapping) -> Iterator[Any]:
    """Yield all values in a nested dictionary in depth-first order."""
    for _, v in items_nested(d):
        yield v


def flatten_dict(
    dictionary: MutableMapping, sep: str = ".", dict_factory: Callable = dict
) -> MutableMapping:
    """
    Flatten a nested dictionary into a single-level dict with concatenated keys.

    Args:
        dictionary (MutableMapping): The nested dictionary to flatten.
        sep (str, optional): Separator between keys. Defaults to '.'.
        dict_factory (Callable, optional): Factory for the output dictionary. Defaults to dict.

    Returns:
        MutableMapping: A new flattened dictionary.

    Example:
        >>> inp = {'a': {'b': 1, 'c': {'d': 2}}, 'e': 3}
        >>> flatten_dict(inp, sep=':')
        {'a:b': 1, 'a:c:d': 2, 'e': 3}
    """
    result = dict_factory()
    for path, value in items_nested(dictionary):
        flat_key = sep.join(path)
        result[flat_key] = value
    return result


def unflatten_dict(
    dictionary: MutableMapping, sep: str = ".", dict_factory: Callable = dict
) -> MutableMapping:
    """
    Reconstruct a nested dictionary from a flattened dictionary.

    Args:
        dictionary (MutableMapping): Flat dictionary with joined keys.
        sep (str, optional): Separator used in flat keys. Defaults to '.'.
        dict_factory (Callable, optional): Factory for intermediate dictionaries. Defaults to dict.

    Returns:
        MutableMapping: A new nested dictionary.

    Example:
        >>> inp = {'a.b': 1, 'a.c.d': 2, 'e': 3}
        >>> unflatten_dict(inp, sep='.')
        {'a': {'b': 1, 'c': {'d': 2}}, 'e': 3}
    """
    result = dict_factory()
    for flat_key, value in dictionary.items():
        keys = flat_key.split(sep)
        set_nested(result, keys, value, subdict_factory=dict_factory)
    return result
