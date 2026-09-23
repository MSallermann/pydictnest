# pydictnest

`pydictnest` is a small, typed Python library for working with nested mappings.
It provides focused helpers for reading, writing, traversing, flattening, and
reconstructing dictionary-like structures.

The package can:

- Get or set a value using a sequence of nested keys.
- Check whether a nested key path exists.
- Iterate over the paths and values of all leaf nodes.
- Flatten a nested mapping into string-keyed entries.
- Reconstruct a nested mapping from flattened keys.
- Read immutable `Mapping` implementations without copying them first.
- Preserve the concrete mutable mapping type produced by a custom factory.

## Installation

Install the latest release from PyPI:

```bash
python -m pip install pydictnest
```

To install the current development version directly from GitHub:

```bash
python -m pip install git+https://github.com/MSallermann/pydictnest.git
```

The package supports Python 3.9 and newer.

## Quick start

```python
from pydictnest import (
    flatten_dict,
    get_nested,
    has_nested,
    items_nested,
    set_nested,
    unflatten_dict,
)

data = {}
set_nested(data, ["model", "parameters", "sigma"], 3.2)
set_nested(data, ["model", "parameters", "epsilon"], 0.8)

assert get_nested(data, ["model", "parameters", "sigma"]) == 3.2
assert get_nested(data, ["metadata", "label"], default="unknown") == "unknown"
assert has_nested(data, ["model", "parameters", "epsilon"])

for path, value in items_nested(data):
    print(path, value)

# ["model", "parameters", "sigma"] 3.2
# ["model", "parameters", "epsilon"] 0.8

flat = flatten_dict(data)
assert flat == {
    "model.parameters.sigma": 3.2,
    "model.parameters.epsilon": 0.8,
}

assert unflatten_dict(flat) == data
```

### Read-only mappings

Operations that only inspect their input accept any `Mapping`, including
immutable mapping proxies:

```python
from types import MappingProxyType

from pydictnest import flatten_dict, get_nested

parameters = MappingProxyType(
    {
        "model": MappingProxyType({"sigma": 3.2, "epsilon": 0.8}),
    }
)

assert get_nested(parameters, ["model", "sigma"]) == 3.2
assert flatten_dict(parameters) == {
    "model.sigma": 3.2,
    "model.epsilon": 0.8,
}
```

Only `set_nested` requires a `MutableMapping`, because it modifies its input.

### Custom output mappings

`flatten_dict` and `unflatten_dict` create regular dictionaries by default.
Pass `dict_factory` to select another mutable mapping type:

```python
from collections import defaultdict

from pydictnest import flatten_dict, unflatten_dict


def mapping_factory():
    return defaultdict(dict)


flat = flatten_dict(
    {"model": {"sigma": 3.2}},
    dict_factory=mapping_factory,
)
nested = unflatten_dict(flat, dict_factory=mapping_factory)

assert isinstance(flat, defaultdict)
assert isinstance(nested, defaultdict)
```

The package includes a `py.typed` marker. Type checkers infer `dict[str, Any]`
for the default output and preserve the concrete return type of a custom
factory.

## API reference

### `set_nested(dictionary, keys, value, subdict_factory=dict)`

Set `value` at the specified key path. Missing intermediate mappings are
created with `subdict_factory`. Existing non-mutable intermediate values are
replaced. An empty key path raises `ValueError`.

### `get_nested(dictionary, keys, default=None)`

Return the value at a key path. If any part of the path is missing or is not a
mapping, return `default`. An empty key path raises `ValueError`.

### `has_nested(dictionary, keys)`

Return whether the complete key path exists. An empty key path raises
`ValueError`.

### `items_nested(dictionary, subkeys=None)`

Yield `(path, value)` pairs for every leaf node in depth-first insertion order.
Each path is returned as a `list[str]`. `subkeys` is primarily used internally
to continue a traversal from an existing path.

### `keys_nested(dictionary)`

Yield the `list[str]` path of every leaf node.

### `values_nested(dictionary)`

Yield every leaf value in depth-first insertion order.

### `flatten_dict(dictionary, sep=".", dict_factory=dict)`

Join each leaf path with `sep` and return a new flat mutable mapping. The input
is not modified. The default result is a `dict`; a custom `dict_factory`
controls the concrete output type.

### `unflatten_dict(dictionary, sep=".", dict_factory=dict)`

Split each flat key on `sep` and reconstruct a nested mutable mapping. The
default result is a `dict`; a custom `dict_factory` is used for both the root
and intermediate mappings.

## Flattening constraints

Keys must be strings. The separator is not escaped, so a key that already
contains `sep` cannot be distinguished from a nested path during unflattening.
Empty nested mappings also contain no leaf to emit and therefore are not
preserved by a flatten/unflatten round trip.

Choose a separator that cannot occur in the source keys when round-trip
reconstruction is required.

## Development

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/MSallermann/pydictnest.git
cd pydictnest
python -m pip install -e .
```

Run the runtime, typing, and lint checks with:

```bash
pytest
pyright
ruff check .
ruff format --check .
```

Alternatively, `nox` runs the test suite across the supported Python versions
available on the system and executes the Pyright session.

Contributions and bug reports are welcome through the project repository.

## License

`pydictnest` is distributed under the MIT License. See [LICENSE](LICENSE) for
details.
