# Copied from the Requests library by Kenneth Reitz et al.
#
# Copyright 2013 Kenneth Reitz
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import collections
if False:
    from typing import Any, Iterable, Iterator, Mapping, Tuple, Union


# TODO(kgriffs): If we ever diverge from what is upstream in Requests,
# then we will need write tests and remove the "no cover" pragma.
class CaseInsensitiveDict(collections.MutableMapping):  # pragma: no cover
    """
    A case-insensitive ``dict``-like object.

    Implements all methods and operations of
    ``collections.MutableMapping`` as well as dict's `copy`. Also
    provides `lower_items`.

    All keys are expected to be strings. The structure remembers the
    case of the last key to be set, and ``iter(instance)``,
    ``keys()``, ``items()``, ``iterkeys()``, and ``iteritems()``
    will contain case-sensitive keys. However, querying and contains
    testing is case insensitive:

        cid = CaseInsensitiveDict()
        cid['Accept'] = 'application/json'
        cid['aCCEPT'] == 'application/json'  # True
        list(cid) == ['Accept']  # True

    For example, ``headers['content-encoding']`` will return the
    value of a ``'Content-Encoding'`` response header, regardless
    of how the header name was originally stored.

    If the constructor, ``.update``, or equality comparison
    operations are given keys that have equal ``.lower()``s, the
    behavior is undefined.

    """
    def __init__(self, data=None, **kwargs):
        # type: (Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]], **Any) -> None  # NOQA
        self._store = dict()  # type: dict
        if data is None:
            data = {}
        #TODO(tim.simpson): There is oddness in typeshed re: MutableMapping.
        self.update(data, **kwargs)  # type: ignore

    def __setitem__(self, key, value):
        # type: (str, Any) -> None
        # Use the lowercased key for lookups, but store the actual
        # key alongside the value.
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        # type: (str) -> Any
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        # type: (str) -> None
        del self._store[key.lower()]

    def __iter__(self):
        # type: () -> Iterator
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        # type: () -> int
        return len(self._store)

    def lower_items(self):
        # type: () -> Iterable[Tuple[str, Any]]
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, keyval[1])
            for (lowerkey, keyval)
            in self._store.items()
        )

    def __eq__(self, other):
        # type: (Any) -> Union[bool, NotImplemented]
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    # Copy is required
    def copy(self):
        # type: () -> CaseInsensitiveDict
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        # type: () -> str
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))
