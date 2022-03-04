# Copyright (c) 2013-2018    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

from lxml import etree as ET
import six

from .pg import Link
from .. import namespaces as GNS
from .pg import Namespaces as PGNS
from ..model.util import XPathXRange

_XPNS = {'g' : GNS.REQUEST.name, 's' : GNS.SVLAN.name, 'e' : PGNS.EMULAB.name,
                 'i' : PGNS.INFO.name, 'p' : PGNS.PARAMS.name, 'u' : GNS.USER.name}

class ManifestLink(Link):
    def __init__(self):
        super()

        self.interface_refs = []
        self.sliver_id = None
        self.vlan = None
        self._elem = None

    @classmethod
    def _fromdom(cls, elem):
        lnk = ManifestLink()
        lnk._elem = elem
        lnk.client_id = elem.get("client_id")
        lnk.sliver_id = elem.get("sliver_id")
        lnk.vlan = elem.get("vlantag", None)

        refs = elem.xpath('g:interface_ref', namespaces = _XPNS)
        for ref in refs:
            lnk.interface_refs.append(ref.get("sliver_id"))

        svlans = elem.xpath('s:link_shared_vlan', namespaces = _XPNS)
        if svlans:
            # TODO: Can a link be attached to more than one shared vlan?
            # Don't believe PG supports trunks, but the rspec doesn't really forbid it
            lnk.vlan = svlans[0].get("name")

        return lnk

    @property
    def text(self):
        return ET.tostring(self._elem, pretty_print=True).decode()


class ManifestSvcLogin:
    def __init__(self):
        self.auth = None
        self.hostname = None
        self.port = None
        self.username = None

    @classmethod
    def _fromdom(cls, elem):
        n = ManifestSvcLogin()
        n.auth = elem.get("authentication")
        n.hostname = elem.get("hostname")
        n.port = int(elem.get("port"))
        n.username = elem.get("username")

        return n


class ManifestSvcUser:
    def __init__(self):
        self.login = None
        self.public_key = None

    @classmethod
    def _fromdom(cls, elem):
        n = cls()
        n.login = elem.get("login")
        pkelems = elem.xpath('u:public_key', namespaces = _XPNS)
        if pkelems:
            n.public_key = pkelems[0].text.strip()
        return n

class ManifestNode:
    class Interface:
        def __init__(self):
            self.client_id = None
            self.mac_address = None
            self.sliver_id = None
            self.address_info = None
            self.component_id = None

        @property
        def address(self):
            ''' Get the IP address of this interface '''
            addr, _netmask = self.address_info
            return addr

        @property
        def netmask(self):
            ''' Get the netmask used by this interface '''
            _adddr, netmask = self.address_info
            return netmask

    def __init__ (self):
        super()

        self.logins = []
        self.users = []
        self.interfaces = []
        self.client_id = None
        self.component_id = None
        self.sliver_id = None
        self._elem = None
        self._hostfqdn = None
        self._hostipv4 = None

    @property
    def name(self):
        return self.client_id

    @property
    def hostfqdn(self):
        if not self._hostfqdn:
            self._populateHostInfo()
        return self._hostfqdn

    @property
    def hostipv4(self):
        if not self._hostipv4:
            self._populateHostInfo()
        return self._hostipv4

    def _populateHostInfo(self):
        host = self._elem.xpath('g:host', namespaces = _XPNS)
        if host:
            self._hostfqdn = host[0].get("name", None)
            self._hostipv4 = host[0].get("ipv4", None)

    @classmethod
    def _fromdom(cls, elem):
        n = ManifestNode()
        n._elem = elem
        n.client_id = elem.get("client_id")
        n.component_id = elem.get("component_id")
        n.sliver_id = elem.get("sliver_id")

        logins = elem.xpath('g:services/g:login', namespaces = _XPNS)
        for lelem in logins:
            l = ManifestSvcLogin._fromdom(lelem)
            n.logins.append(l)

        users = elem.xpath('g:services/u:services_user', namespaces = _XPNS)
        for uelem in users:
            u = ManifestSvcUser._fromdom(uelem)
            n.users.append(u)

        interfaces = elem.xpath('g:interface', namespaces = _XPNS)
        for ielem in interfaces:
            i = ManifestNode.Interface()
            i.client_id = ielem.get("client_id")
            i.sliver_id = ielem.get("sliver_id")
            i.component_id = ielem.get("component_id")
            i.mac_address = ielem.get("mac_address")
            try:
                ipelem = ielem.xpath('g:ip', namespaces = _XPNS)[0]
                i.address_info = (ipelem.get("address"), ipelem.get("netmask"))
            except Exception:
                pass
            n.interfaces.append(i)

        return n

    @property
    def text(self):
        return ET.tostring(self._root, pretty_print=True).decode()


class ManifestParameter:
    def __init__(self, name, value):
        super()
        self.name = name
        self.value = value

    @staticmethod
    def _process_element(elem):
        retval = None
        if elem.tag == f"{{{PGNS.PARAMS.name}}}data_item":
            retval = elem.text
        elif elem.tag == f"{{{PGNS.PARAMS.name}}}data_list":
            retval = []
            for e in elem:
                retval.append(ManifestParameter._process_element(e))
        elif elem.tag == f"{{{PGNS.PARAMS.name}}}data_struct":
            retval = {}
            for e in elem:
                name = e.get("name").split(".")[-1]
                retval[name] = ManifestParameter._process_element(e)
        elif elem.tag == f"{{{PGNS.PARAMS.name}}}data_member_item":
            retval = elem.text
        else:
            raise Exception(f"unknown parameter tag {elem.tag}")

        return retval

    @classmethod
    def _fromdom (cls, elem):
        name = elem.get("name").split(".")[-1]
        return ManifestParameter(name,ManifestParameter._process_element(elem))

class Manifest:
    REQUESTV2 = "http://www.protogeni.net/resources/rspec/2"

    def __init__(self, path = None, xml = None):
        if path and xml:
            raise RuntimeError("Cannot specify, both, path and xml when opening manifest file")

        if path:
            with open(path, "r", encoding='utf-8') as xmlfile:
                self._xml = xmlfile.read()
        elif xml:
            if six.PY3:
                self._xml = bytes(xml, "utf-8")
            else:
                self._xml = xml

        self._root = ET.fromstring(self._xml)
        self._pid = os.getpid()

    @property
    def root(self):
        if os.getpid() != self._pid:
            self._root = ET.fromstring(self._xml)
            self._pid = os.getpid()
        return self._root

    @property
    def latitude(self):
        loc = self._root.xpath('i:site_info/i:location', namespaces = _XPNS)
        if loc:
            return loc[0].get("latitude")

    @property
    def longitude(self):
        loc = self._root.xpath('i:site_info/i:location', namespaces = _XPNS)
        if loc:
            return loc[0].get("longitude")

    @property
    def expiresstr(self):
        return self._root.get("expires")

    @property
    def links(self):
        llist = self.root.findall(f"{{{GNS.REQUEST}}}link")
        llist.extend(self.root.findall(f"{{{Manifest.REQUESTV2}}}link"))
        return XPathXRange(llist, ManifestLink)

    @property
    def nodes(self):
        nlist = self.root.findall(f"{{{GNS.REQUEST}}}node")
        nlist.extend(self.root.findall(f"{{{Manifest.REQUESTV2}}}node"))
        return XPathXRange(nlist, ManifestNode)

    @property
    def parameters(self):
        for set_elem in self.root.findall(f"{{{PGNS.PARAMS.name}data_set"):
            for param_elem in list(set_elem):
                if not param_elem.tag in [f"{{{PGNS.PARAMS.name}}}data_item",
                                          f"{{{PGNS.PARAMS.name}}}data_list",
                                          f"{{{PGNS.PARAMS.name}}}data_struct"]:
                    continue
                elm = ManifestParameter._fromdom(param_elem)
                yield elm

    @property
    def text(self):
        return ET.tostring(self._root, pretty_print=True).decode()

    def _repr_html_(self):
        return """
<table>
    <tr><th scope="row">Expires</th><td>%s</td></tr>
    <tr><th scope="row">Nodes</th><td>%d</td></tr>
    <tr><th scope="row">Links</th><td>%d</td></tr>
    <tr><th scope="row">Location</th><td>%s, %s</td></tr>
</table>""" % (self.expiresstr, len(self.nodes), len(self.links),
                             self.latitude, self.longitude)

    def write (self, path):
        """
.. deprecated:: 0.4
        Use :py:meth:`geni.rspec.pg.Request.writeXML` instead."""

        import geni.warnings as GW
        import warnings
        warnings.warn("The Manifest.write() method is deprecated, please use Manifest.writeXML() instead",
                                    GW.GENILibDeprecationWarning, 2)
        self.writeXML(path)

    def writeXML(self, path):
        """Write the current manifest as an XML file that contains an rspec in the format returned by the
        aggregate."""
        with open(path, "w+", encoding='utf-8') as xmlfile:
            xmlfile.write(ET.tostring(self.root, pretty_print=True))
