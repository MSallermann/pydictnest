from collections.abc import MutableMapping, Sequence
from typing import Any


def set_nested_value(
    dictionary: MutableMapping, keys: Sequence[str], value: Any, subdict_factory=dict
) -> None:
    # Base case: just insert
    if len(keys) <= 1:
        dictionary[keys[0]] = value
    else:
        # recursion
        first_key = keys[0]
        if first_key not in dictionary:
            # use subdict_factory to create a new subdict if necessary
            dictionary[first_key] = subdict_factory()
        set_nested_value(dictionary=dictionary[first_key], keys=keys[1:], value=value)


def has_nested_value(dictionary: MutableMapping, keys: Sequence[str]) -> bool:
    # Base case
    if len(keys) <= 1:
        return keys[0] in dictionary
    else:
        first_key = keys[0]
        return get_nested_value(dictionary=dictionary[first_key], keys=keys[1:])


def get_nested_value(
    dictionary: MutableMapping, keys: Sequence[str], default: Any = None
) -> Any:
    # Base case
    if len(keys) <= 1:
        return dictionary.get(keys[0], default)
    else:
        first_key = keys[0]
        return get_nested_value(
            dictionary=dictionary[first_key], keys=keys[1:], default=default
        )


def iterate_nested_dict(d: MutableMapping, subkeys: Sequence[str] = []):
    """Iterates over a nested dict

    Args:
        dictionary (dict): The input dictionary
        subkeys (Sequence[str], optional): The current Sequence of subkeys. Only used for the recursive implementation

    Example:
        >>> inp = {"a": {"b": 1.0, "c": 2.0, "d": {"e": "test"}}, "f": [1, 2]}
        >>> for keys, value in iterate_nested_dict(inp):
        >>>     print(keys, value)
        >>> ['a', 'b'] 1.0
            ['a', 'c'] 2.0
            ['a', 'd', 'e'] test
            ['f'] [1, 2]
    """

    for key, value in d.items():
        if isinstance(value, MutableMapping):
            yield from iterate_nested_dict(
                value, subkeys=subkeys + [key]
            )  # Recursively yield from sub-dictionary
        else:
            yield subkeys + [key], value


def flatten_dict(dictionary: MutableMapping, sep: str = ".", dict_factory=dict) -> dict:
    """Flatten a nested dictionary into a flat dictionary by inserting a separator between sub keys.

    Args:
        dictionary (dict): The input dictionary
        separator (str, optional): The separator to insert between keys. Defaults to ".".

    Returns:
        dict: flattened dictionary

    Example:
        >>> inp = {"a": {"b": 1.0, "c": 2.0, "d": {"e": "test"}}, "f": [1, 2]}
        >>> out = flatten_dict(inp, sep=".")
        >>> print(out)
        >>> {'a.b': 1.0, 'a.c': 2.0, 'a.d.e': 'test', 'f': [1, 2]}
    """
    res = dict_factory
    for keys, value in iterate_nested_dict(dictionary):
        key_out = sep.join(keys)
        res[key_out] = value
    return res


def unflatten_dict(
    dictionary: dict, sep: str = ".", dict_factory=dict
) -> MutableMapping:
    """Unflatten a dictionary by assuming subkeys are separated by a separator

    Args:
        dictionary (dict): The input dictionary
        sep (str, optional): The separator. Defaults to ".".

    Returns:
        dict: The unflattened output dictionary

    Example:
        >>> inp = {'a.b': 1.0, 'a.c': 2.0, 'a.d.e': 'test', 'f': [1, 2]}
        >>> out = unflatten_dict(inp, sep=".")
        >>> print(out)
        >>> {"a": {"b": 1.0, "c": 2.0, "d": {"e": "test"}}, "f": [1, 2]}
    """
    res = dict_factory
    for key, value in dictionary.items():
        subkeys = key.split(sep)
        set_nested_value(dictionary=res, keys=subkeys, value=value)
    return res
