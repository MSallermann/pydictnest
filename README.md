# Pydictnest

Nothing fancy. Just a lightweight Python package for some basic work with nested dictionaries. Provides functions to set, get, check, flatten, and unflatten values in arbitrarily deep mappings, plus iteration over nested structures.

* **Get and Set** Get and set values based on a list of keys in nested mappings
* **Check** whether a nested path exists.
* **Iterate** over all (path, value) pairs in a nested mapping.
* **Flatten** a nested dict to a single-level dict with concatenated keys.
* **Unflatten** a flat dict back into a nested structure.

## Installation

Install via pip with

```bash
pip install pydictnest
```

or from the newest source with

```bash
pip install git+https://github.com/MSallermann/pydictnest.git
```

You can also clone the repo and install locally

```bash
git clone https://github.com/MSallermann/pydictnest.git
cd pydictnest
pip install .
```

## Usage

Should be quite obvious. Here is a small writeup (mostly take from the unit test):

```python
from pydictnest import (
    set_nested, get_nested, has_nested,
    items_nested, flatten_dict, unflatten_dict
)

# Start with an empty dict
data = {}
set_nested(data, ['a', 'b', 'c'], 123)
# data == {'a': {'b': {'c': 123}}}

# Retrieve values
val = get_nested(data, ['a', 'b', 'c'])        # 123
missing = get_nested(data, ['x', 'y'], default=0) # 0

# Check existence
assert has_nested(data, ['a', 'b', 'c'])
assert not has_nested(data, ['a', 'z'])

# Iterate over all leaf nodes
for path, value in items_nested(data):
    print(path, value)
    # ['a', 'b', 'c'] 123

# Flatten and unflatten
nested = {'x': {'y': 1, 'z': {'w': 2}}, 'u': 3}
flat = flatten_dict(nested, sep='.')
# flat == {'x.y': 1, 'x.z.w': 2, 'u': 3}

roundtrip = unflatten_dict(flat, sep='.')
# roundtrip == nested
```

## API Reference

### `set_nested(dictionary, keys, value, subdict_factory=dict)`

Set a value at the specified nested key-path, creating sub-dicts with `subdict_factory`.

### `get_nested(dictionary, keys, default=None)`

Retrieve a deep value, returning `default` if any key is missing.

### `has_nested(dictionary, keys)`

Return `True` if a deep key-path exists, otherwise `False`.

### `items_nested(d, subkeys=[])`

Yields `(key_path, value)` tuples for each leaf node in a nested mapping.

### `keys_nested(d)`

Yields `key_path` for each leaf node in a nested mapping.

### `values_nested(d)`

Yields `value` for each leaf node in a nested mapping.

### `flatten_dict(dictionary, sep='.', dict_factory=dict)`

Convert a nested dict into a flat dict by joining keys with `sep`.

### `unflatten_dict(dictionary, sep='.', dict_factory=dict)`

Reconstruct a nested mapping from a flat dict with joined keys.

## Running Tests

This project uses pytest. To run the test suite:

```bash
pytest
```

## Rationale

Not much of a rationale really. Needed this for a small project and wanted something lightweight.

## Contributing

Make a PR if you want to contribute anything.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
