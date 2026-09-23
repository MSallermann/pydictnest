from __future__ import annotations

from collections import UserDict, defaultdict
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from pydictnest import (
    flatten_dict,
    get_nested,
    has_nested,
    items_nested,
    keys_nested,
    unflatten_dict,
    values_nested,
    set_nested,
)

if TYPE_CHECKING:
    source: Mapping[str, object] = MappingProxyType({"a": {"b": 1}})

    flattened: dict[str, Any] = flatten_dict(source)
    reconstructed: dict[str, Any] = unflatten_dict(MappingProxyType({"a.b": 1}))

    def defaultdict_factory() -> defaultdict[str, Any]:
        return defaultdict(dict)

    custom_flattened: defaultdict[str, Any] = flatten_dict(
        source,
        dict_factory=defaultdict_factory,
    )
    custom_reconstructed: defaultdict[str, Any] = unflatten_dict(
        MappingProxyType({"a.b": 1}),
        dict_factory=defaultdict_factory,
    )

    has_nested(source, ["a", "b"])
    get_nested(source, ["a", "b"])
    items_nested(source)
    keys_nested(source)
    values_nested(source)

    mutable_mapping: UserDict[str, Any] = UserDict()
    set_nested(mutable_mapping, ["a", "b"], 1)

    flatten_dict(["not", "a", "mapping"])  # pyright: ignore[reportArgumentType]
