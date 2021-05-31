 # Copyright (c) 2014-2016    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class User:
    def __init__ (self):
        self.name = None
        self.urn = None
        self._keys = []

    @property
    def keys(self):
        return self._keys

    def add_key(self, path):
        self._keys.append(path)
