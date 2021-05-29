# Copyright (c) 2013    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from lxml import etree as ET
import geni.namespaces as GNS

class RSpec:
    def __init__ (self, rtype):
        self._ns_map = {}
        self._nsnames = set()
        self._loclist = []
        self.add_namespace(GNS.XSNS)
        self.type = rtype

    def add_namespace(self, nspace, prefix = ""):
        if nspace.name in self._nsnames:
            return

        self._nsnames.add(nspace.name)

        if prefix != "":
            self._ns_map[prefix] = nspace.name
        else:
            self._ns_map[nspace.prefix] = nspace.name

        if nspace.location is not None:
            self._loclist.append(nspace.name)
            self._loclist.append(nspace.location)

    def to_xml_string (self, pretty_print = False):
        rspec = self.get_dom()
        return ET.tostring(rspec, pretty_print=pretty_print).decode()

    def get_dom(self):
        rspec = ET.Element("rspec", nsmap=self._ns_map)
        rspec.attrib["{%s}schemaLocation" % (GNS.XSNS.name)] = " ".join(self._loclist)
        rspec.attrib["type"] = self.type
        return rspec
