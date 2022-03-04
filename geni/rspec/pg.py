# Copyright (c) 2013-2017    Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# pylint: disable=too-many-instance-attributes,c-extension-no-member

import itertools
import sys
import functools
from enum import Enum

from lxml import etree as ET
import six

import geni.warnings as GW
import warnings

import geni.rspec
import geni.namespaces as GNS
import geni.urn

# This exception gets thrown if a __ONCEONLY__ extension gets added to a parent
# element more than one time
class DuplicateExtensionError(Exception):
    def __init__(self, klass):
        super().__init__()
        self.klass = klass

    def __str__(self):
        return "Extension (%s) can only be added to a parent object once" % self.klass.__name__

################################################
# Base Request - Must be at top for EXTENSIONS #
################################################
class Request(geni.rspec.RSpec):
    EXTENSIONS = []

    def __init__(self):
        super().__init__("request")
        self._resources = []
        self.tour = None
        self._raw_elements = []

        self.add_namespace(GNS.REQUEST, None)
        self.add_namespace(Namespaces.CLIENT)

        self._ext_children = []
        for name,ext in Request.EXTENSIONS:
            self._wrapext(name,ext)

    def _wrapext(self, name, klass):
        @functools.wraps(klass.__init__)
        def wrap(*args, **kw):
            if getattr(klass, "__ONCEONLY__", False):
                if any(map(lambda x: isinstance(x,klass),self._ext_children)):
                    raise DuplicateExtensionError(klass)
            instance = klass(*args, **kw)
            if getattr(klass, "__WANTPARENT__", False):
                instance._parent = self
            self._ext_children.append(instance)
            return instance
        setattr(self, name, wrap)

    def add_resource(self, rsrc):
        for nspace in rsrc.namespaces:
            self.add_namespace(nspace)
        self._resources.append(rsrc)

    @property
    def resources(self):
        return self._resources + self._ext_children

    def add_tour(self, tour):
        self.add_namespace(Namespaces.EMULAB)
        self.add_namespace(Namespaces.JACKS)
        self.tour = tour

    def has_tour(self):
        return self.tour is not None

    def add_raw_element(self, elem):
        self._raw_elements.append(elem)

    def write_xml(self, path):
        """Write the current request contents as an XML file that represents an rspec
        in the GENIv3 format."""

        buf = self.to_xml_string(pretty_print=True)

        if path is None:
            sys.stdout.write(buf)
        else:
            with open(path, "w+", encoding='utf-8') as outfile:
                outfile.write(buf)

    def to_xml_string(self, pretty_print=False):
        """Return the current request contents as an XML string that represents an rspec
        in the GENIv3 format."""

        rspec = self.get_dom()

        if self.tour:
            self.tour._write(rspec)

        for resource in self._resources:
            resource._write(rspec)

        for obj in self._ext_children:
            obj._write(rspec)

        for elem in self._raw_elements:
            rspec.append(elem)

        return ET.tostring(rspec, pretty_print=pretty_print).decode()


class Resource:
    def __init__(self):
        self.namespaces = []
        self._ext_children = []

    def add_namespace(self, nspace):
        self.namespaces.append(nspace)

    def _wrapext(self, name, klass):
        @functools.wraps(klass.__init__)
        def wrap(*args, **kw):
            if getattr(klass, "__ONCEONLY__", False):
                if any(map(lambda x: isinstance(x,klass),self._ext_children)):
                    raise DuplicateExtensionError(klass)
            instance = klass(*args, **kw)
            self._ext_children.append(instance)
            return instance
        setattr(self, name, wrap)

    def _write(self, element):
        for obj in self._ext_children:
            obj._write(element)
        return element


class NodeType(Enum):
    XEN = "emulab-xen"
    DOCKER = "emulab-docker"
    RAW_PC = "raw-pc"
    VM = "emulab-xen"

class Command:
    def __init__(self, cmd, data):
        self._cmd = cmd
        self.data = data

    @property
    def cmd(self):
        return self._cmd

    def resolve(self):
        return self.cmd % self.data


class Service:
    def __init__(self):
        pass


class Install(Service):
    def __init__(self, url, path):
        super().__init__()
        self.url = url
        self.path = path

    def _write(self, element):
        ins = ET.SubElement(element, "{%s}install" % (GNS.REQUEST.name))
        ins.attrib["url"] = self.url
        ins.attrib["install_path"] = self.path
        return ins


class Execute(Service):
    def __init__(self, shell, command):
        super().__init__()
        self.shell = shell
        self._command = command

    @property
    def command(self):
        return self._command

    def _write(self, element):
        exc = ET.SubElement(element, "{%s}execute" % (GNS.REQUEST.name))
        exc.attrib["shell"] = self.shell
        if isinstance(self.command, Command):
            exc.attrib["command"] = self.command.resolve()
        else:
            exc.attrib["command"] = self.command
        return exc


class Address:
    def __init__(self, atype):
        self.type = atype


class IPv4Address(Address):
    def __init__(self, address, netmask):
        super().__init__("ipv4")
        self.address = address
        self.netmask = netmask

    def _write(self, element):
        ip = ET.SubElement(element, "{%s}ip" % (GNS.REQUEST.name))
        ip.attrib["address"] = self.address
        ip.attrib["netmask"] = self.netmask
        ip.attrib["type"] = self.type
        return ip


class Interface:
    EXTENSIONS = []

    class InvalidAddressTypeError(Exception):
        def __init__ (self, addr):
            super().__init__()
            self.addr = addr
        def __str__ (self):
            return "Type (%s) is invalid for interface addresses." % (type(self.addr))

    def __init__(self, name, node, address = None):
        self.client_id = name
        self.node = node
        self.addresses = []
        self.component_id = None
        self.bandwidth = None
        self.latency = None
        self.plr = None
        self._ext_children = []

        if address:
            self.add_address(address)

        for iname, ext in Interface.EXTENSIONS:
            self._wrapext(iname, ext)

    def _wrapext(self, name, klass):
        @functools.wraps(klass.__init__)
        def wrap(*args, **kw):
            if getattr(klass, "__ONCEONLY__", False):
                if any(map(lambda x: isinstance(x,klass),self._ext_children)):
                    raise DuplicateExtensionError(klass)
            instance = klass(*args, **kw)
            if getattr(klass, "__WANTPARENT__", False):
                instance._parent = self
            self._ext_children.append(instance)
            return instance
        setattr(self, name, wrap)

    @property
    def name(self):
        return self.client_id

    def add_address(self, address):
        if isinstance(address, Address):
            self.addresses.append(address)
        else:
            raise Interface.InvalidAddressTypeError(address)

    def _write(self, element):
        intf = ET.SubElement(element, "{%s}interface" % (GNS.REQUEST.name))
        intf.attrib["client_id"] = self.client_id
        if self.component_id:
            if isinstance(self.component_id, geni.urn.Base):
                intf.attrib["component_id"] = str(self.component_id)
            else:
                intf.attrib["component_id"] = self.component_id
        for addr in self.addresses:
            addr._write(intf)
        for obj in self._ext_children:
            obj._write(intf)
        return intf


class Link(Resource):
    EXTENSIONS = []
    LNKID = 0
    DEFAULT_BW = -1
    DEFAULT_LAT = 0
    DEFAULT_PLR = 0.0

    def __init__(self, name = None, ltype = "", members = None):
        super().__init__()

        if name is None:
            self._client_id = Link.new_link_id()
        else:
            self._client_id = name

        self.interfaces = []

        if members is not None:
            for member in members:
                if isinstance(member,Interface):
                    self.add_interface(member)
                else:
                    self.add_interface(member.add_interface())

        self.type = ltype
        self.shared_vlan = None
        self._mac_learning = True
        self._vlan_tagging = None
        self._trivial_ok = None
        self._link_multiplexing = False
        self._best_effort = False
        self._ext_children = []
        self._raw_elements = []
        self._component_managers = []
        self.protocol = None

        # If you try to set bandwidth higher than a gigabit, PG probably won't like you
        self.bandwidth = Link.DEFAULT_BW
        self.latency = Link.DEFAULT_LAT
        self.plr = Link.DEFAULT_PLR

        for iname,ext in Link.EXTENSIONS:
            self._wrapext(iname,ext)

    def _wrapext(self, name, klass):
        @functools.wraps(klass.__init__)
        def wrap(*args, **kw):
            if getattr(klass, "__ONCEONLY__", False):
                if any(map(lambda x: isinstance(x,klass),self._ext_children)):
                    raise DuplicateExtensionError(klass)
            instance = klass(*args, **kw)
            if getattr(klass, "__WANTPARENT__", False):
                instance._parent = self
            self._ext_children.append(instance)
            return instance
        setattr(self, name, wrap)

    def add_raw_element(self, elem):
        self._raw_elements.append(elem)

    @classmethod
    def new_link_id(cls):
        Link.LNKID += 1
        return "link-%d" % (Link.LNKID)

    def add_child(self, obj):
        self._ext_children.append(obj)

    def add_interface(self, intf):
        self.interfaces.append(intf)

    def add_node(self, node):
        interface = node.add_interface()
        self.interfaces.append(interface)
        return interface

    def add_component_manager(self, component_manager):
        self._component_managers.append(component_manager)

    def connect_shared_vlan(self, arg):
        self.namespaces.append(GNS.SVLAN)

        if isinstance(arg, LAN):
            self.shared_vlan = arg.client_id
        elif isinstance(arg, str):
            self.shared_vlan = arg
        else:
            raise ValueError("Expected LAN or str")

    def disable_mac_learning(self):
        self.namespaces.append(Namespaces.VTOP)
        self._mac_learning = False

    def enable_vlan_tagging(self):
        warnings.warn("Link.enableVlanTagging() is deprecated, please use the Link.vlan_tagging attribute instead.",
                                    GW.GENILibDeprecationWarning, 2)
        self.vlan_tagging = True

    @property
    def vlan_tagging(self):
        return self._vlan_tagging

    @property
    def client_id(self):
        return self._client_id

    @vlan_tagging.setter
    def vlan_tagging(self, val):
        self.namespaces.append(Namespaces.EMULAB)
        self._vlan_tagging = val

    @property
    def best_effort(self):
        return self._best_effort

    @best_effort.setter
    def best_effort(self, val):
        self.namespaces.append(Namespaces.EMULAB)
        self._best_effort = val

    @property
    def link_multiplexing(self):
        return self._link_multiplexing

    @link_multiplexing.setter
    def link_multiplexing(self, val):
        self.namespaces.append(Namespaces.EMULAB)
        self._link_multiplexing = val

    @property
    def trivial_ok(self):
        return self._trivial_ok

    @trivial_ok.setter
    def trivial_ok(self, val):
        self.namespaces.append(Namespaces.EMULAB)
        self._trivial_ok = val

    def _write(self, element):
        # pylint: disable=too-many-branches
        lnk = ET.SubElement(element, "{%s}link" % (GNS.REQUEST.name))
        lnk.attrib["client_id"] = self.client_id
        if self.protocol:
            lnk.attrib["protocol"] = self.protocol

        for intf in self.interfaces:
            ir = ET.SubElement(lnk, "{%s}interface_ref" % (GNS.REQUEST.name))
            ir.attrib["client_id"] = intf.client_id
        if self.type != "":
            lt = ET.SubElement(lnk, "{%s}link_type" % (GNS.REQUEST.name))
            lt.attrib["name"] = self.type
        if self.shared_vlan:
            sv = ET.SubElement(lnk, "{%s}link_shared_vlan" % (GNS.SVLAN.name))
            sv.attrib["name"] = self.shared_vlan

        if not self._mac_learning:
            lrnelem = ET.SubElement(lnk, "{%s}link_attribute" % (Namespaces.VTOP.name))
            lrnelem.attrib["key"] = "nomac_learning"
            lrnelem.attrib["value"] = "yep"

        # Do not want to spit out a vlan tagging statement unless explicitly
        # set, since the default is no tagging and always spitting that out
        # will be bad for regression testing.
        if self._vlan_tagging != None:
            tagging = ET.SubElement(lnk, "{%s}vlan_tagging" % (Namespaces.EMULAB.name))
            if self._vlan_tagging:
                tagging.attrib["enabled"] = "true"
            else:
                tagging.attrib["enabled"] = "false"

        if self._best_effort:
            tagging = ET.SubElement(lnk, "{%s}best_effort" % (Namespaces.EMULAB.name))
            tagging.attrib["enabled"] = "true"

        if self._link_multiplexing:
            tagging = ET.SubElement(lnk, "{%s}link_multiplexing" % (Namespaces.EMULAB.name))
            tagging.attrib["enabled"] = "true"

        if self._trivial_ok is not None:
            trivial = ET.SubElement(lnk, "{%s}trivial_ok" % (Namespaces.EMULAB.name))
            if self._trivial_ok:
                trivial.attrib["enabled"] = "true"
            else:
                trivial.attrib["enabled"] = "false"

        # LAN shaping properties are handled by the LAN class below.
        if self.type != "lan":
            for (intf_a, intf_b) in itertools.permutations(self.interfaces,2):
                bandwidth = intf_a.bandwidth if intf_a.bandwidth else self.bandwidth
                lat = intf_a.latency if intf_a.latency else self.latency
                plr = intf_a.plr if intf_a.plr else self.plr
                self._write_link_prop(lnk, intf_b.client_id, intf_a.client_id, bandwidth, lat, plr)

        for obj in self._ext_children:
            obj._write(lnk)

        for elem in self._raw_elements:
            lnk.append(elem)

        for manager in self._component_managers:
            comp = ET.SubElement(lnk, "{%s}component_manager" % (GNS.REQUEST.name))
            comp.attrib["name"] = manager

        return lnk

    def _write_link_prop(self, lnk, src, dst, bw, lat, plr):
        if bw != Link.DEFAULT_BW or lat != Link.DEFAULT_LAT or plr != Link.DEFAULT_PLR:
            prop = ET.SubElement(lnk, "{%s}property" % (GNS.REQUEST.name))
            prop.attrib["source_id"] = src
            prop.attrib["dest_id"] = dst
            if bw != Link.DEFAULT_BW:
                prop.attrib["capacity"] = str(bw)
            if lat != Link.DEFAULT_LAT:
                prop.attrib["latency"] = str(lat)
            if plr != Link.DEFAULT_PLR:
                prop.attrib["packet_loss"] = str(plr)

Request.EXTENSIONS.append(("Link", Link))


class LAN(Link):
    def __init__(self, name = None):
        super().__init__(name, "lan")

    def _write(self, element):
        lnk = super()._write(element)

        for intf in self.interfaces:
            bandwidth = intf.bandwidth if intf.bandwidth else self.bandwidth
            latency = intf.latency if intf.latency else self.latency
            plr = intf.plr if intf.plr else self.plr

            super()._write_link_prop(lnk, intf.client_id, self.client_id, bandwidth, latency, plr)

        return lnk

Request.EXTENSIONS.append(("LAN", LAN))


class L3GRE(Link):
    def __init__ (self, name = None):
        super().__init__(name, "gre-tunnel")

Request.EXTENSIONS.append(("L3GRE", L3GRE))

class L2GRE(Link):
    def __init__ (self, name = None):
        super().__init__(name, "egre-tunnel")

Request.EXTENSIONS.append(("L2GRE", L2GRE))

class StitchedLink(Link):
    class UnknownComponentManagerError(Exception):
        def __init__ (self, cid):
            super().__init__()
            self._cid = cid

        def __str__ (self):
            return "Interface with client_id %s is not attached to a bound node." % (self._cid)

    class TooManyInterfacesError(Exception):
        def __str__ (self):
            return "Stitched Links may not be connected to more than two interfaces"

    def __init__ (self, name = None):
        super().__init__(name, "")
        self.bandwidth = 20000

    def _write (self, element):
        if len(self.interfaces) > 2:
            raise StitchedLink.TooManyInterfacesError()

        lnk = super()._write(element)
        for intf in self.interfaces:
            if intf.node.component_manager_id is None:
                raise StitchedLink.UnknownComponentManagerError(intf.client_id)
            comp = ET.SubElement(lnk, "{%s}component_manager" % (GNS.REQUEST.name))
            comp.attrib["name"] = intf.node.component_manager_id
        return lnk

Request.EXTENSIONS.append(("StitchedLink", StitchedLink))

class Node(Resource):
    """A basic Node class.    Typically you want to instantiate one of its subclasses, such as `RawPC`, `XenVM`, or `DockerContainer`.

    Args:
        name (str): Your name for this node.    This must be unique within a single `Request` object.
        ntype (str): The physical or virtual machine type to which this node should be mapped.
        component_id (Optional[str]): The `component_id` of the site physical node to which you want to bind this node.
        exclusive (Optional[bool]): Request this container on an isolated host used only by your sliver.    Defaults to unspecified, allowing the site processing the request rspec to assign resources as it prefers.

    Attributes:
        client_id (str): Your name for this node.    This must be unique within a single `Request` object.
        component_id (Optional[str]): The `component_id` of the site physical node to which you want to bind this node.
        exclusive (Optional[bool]): Request this container on an isolated host used only by your sliver.    Defaults to unspecified, allowing the site processing the request rspec to assign resources as it prefers.
        disk_image (Optional[str]): The disk image that should be loaded and run on this node.    Should be an image URN.
    """
    EXTENSIONS = []

    def __init__(self, name, ntype, component_id = None, exclusive = None):
        super().__init__()
        self.client_id = name
        self.exclusive = exclusive
        self.disk_image = None
        self.type = ntype
        self.hardware_type = None
        self.interfaces = []
        self.services = []
        self.routable_control_ip = False
        self.component_id = component_id
        self.component_manager_id = None
        self._ext_children = []

        for iname, ext in Node.EXTENSIONS:
            self._wrapext(iname, ext)

        self._raw_elements = []

    class DuplicateInterfaceName(Exception):
        def __str__ (self):
            return "Duplicate interface names"

    def _wrapext (self, name, klass):
        @functools.wraps(klass.__init__)
        def wrap(*args, **kw):
            if getattr(klass, "__ONCEONLY__", False):
                if any(map(lambda x: isinstance(x,klass),self._ext_children)):
                    raise DuplicateExtensionError(klass)
            instance = klass(*args, **kw)
            if getattr(klass, "__WANTPARENT__", False):
                instance._parent = self
            self._ext_children.append(instance)
            return instance

        setattr(self, name, wrap)

    @property
    def name (self):
        return self.client_id

    def _write(self, root):
        # pylint: disable=too-many-branches
        nd = ET.SubElement(root, "{%s}node" % (GNS.REQUEST.name))
        nd.attrib["client_id"] = self.client_id
        if self.exclusive is not None:    # Don't write this for EG
            nd.attrib["exclusive"] = str(self.exclusive).lower()
        if self.component_id:
            if isinstance(self.component_id, geni.urn.Base):
                nd.attrib["component_id"] = str(self.component_id)
            else:
                nd.attrib["component_id"] = self.component_id
        if self.component_manager_id:
            if isinstance(self.component_manager_id, geni.urn.Base):
                nd.attrib["component_manager_id"] = str(self.component_manager_id)
            else:
                nd.attrib["component_manager_id"] = self.component_manager_id

        st = ET.SubElement(nd, "{%s}sliver_type" % (GNS.REQUEST.name))
        st.attrib["name"] = self.type

        if self.disk_image:
            # TODO: Force disk images to be objects, and stop supporting old style strings
            if isinstance(self.disk_image, (six.string_types)):
                di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
                di.attrib["name"] = self.disk_image
            elif isinstance(self.disk_image, geni.urn.Base):
                di = ET.SubElement(st, "{%s}disk_image" % (GNS.REQUEST.name))
                di.attrib["name"] = str(self.disk_image)
            else:
                self.disk_image._write(st)

        if self.hardware_type:
            hwt = ET.SubElement(nd, "{%s}hardware_type" % (GNS.REQUEST.name))
            hwt.attrib["name"] = self.hardware_type

        if self.interfaces:
            for intf in self.interfaces:
                intf._write(nd)

        if self.services:
            svc = ET.SubElement(nd, "{%s}services" % (GNS.REQUEST.name))
            for service in self.services:
                service._write(svc)

        if self.routable_control_ip:
            ET.SubElement(nd, "{%s}routable_control_ip" % (Namespaces.EMULAB.name))

        for obj in self._ext_children:
            obj._write(nd)

        for elem in self._raw_elements:
            nd.append(elem)

        return nd

    def add_interface(self, name = None, address = None):
        existingNames = [x.name for x in self.interfaces]
        if name is not None:
            if name.find(":") > 0:
                intfName = name
            else:
                intfName = "%s:%s" % (self.client_id, name)
                pass
        else:
            for i in range(0, 100):
                intfName = "%s:if%i" % (self.client_id, i)
                if intfName not in existingNames:
                    break

        if intfName in existingNames:
            raise Node.DuplicateInterfaceName()

        intf = Interface(intfName, self, address)
        self.interfaces.append(intf)
        return intf

    def add_service(self, svc):
        self.services.append(svc)

    def add_raw_element(self, elem):
        self._raw_elements.append(elem)

Request.EXTENSIONS.append(("Node", Node))

class RawPC(Node):
    def __init__(self, name, component_id = None):
        super().__init__(name, NodeType.RAW_PC.value, component_id=component_id, exclusive=True)

Request.EXTENSIONS.append(("RawPC", RawPC))

class VZContainer(Node):
    def __init__(self, name, exclusive = False):
        super().__init__(name, "emulab-openvz", exclusive)

class Namespaces:
    CLIENT = GNS.Namespace("client", "http://www.protogeni.net/resources/rspec/ext/client/1")
    RS = GNS.Namespace("rs", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
    EMULAB = GNS.Namespace("emulab", "http://www.protogeni.net/resources/rspec/ext/emulab/1")
    VTOP    = GNS.Namespace("vtop", "http://www.protogeni.net/resources/rspec/ext/emulab/1", "vtop_extension.xsd")
    TOUR =    GNS.Namespace("tour", "http://www.protogeni.net/resources/rspec/ext/apt-tour/1")
    JACKS = GNS.Namespace("jacks", "http://www.protogeni.net/resources/rspec/ext/jacks/1")
    INFO = GNS.Namespace("info", "http://www.protogeni.net/resources/rspec/ext/site-info/1")
    PARAMS = GNS.Namespace("parameters", "http://www.protogeni.net/resources/rspec/ext/profile-parameters/1")
    DATA = GNS.Namespace("data", "http://www.protogeni.net/resources/rspec/ext/user-data/1")
    DELAY =    GNS.Namespace("delay", "http://www.protogeni.net/resources/rspec/ext/delay/1")
