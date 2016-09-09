# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Common set of RSpec extensions supported by many Emulab-based aggregates
"""

from __future__ import absolute_import

from ..pg import Request, Namespaces, Link, Node
from lxml import etree as ET

class EmulabExtensionDuplicateStatement(Exception):
    """This exception gets thrown if something that was only supposed to get
    added once to a Request, Node, Link, etc. gets added multiple times."""
    def __init__ (self, classname):
        self._classname = classname

    def __str__ (self):
        return "%s may be used only once!" % str(self._classname,)

class setCollocateFactor(object):
    """Added to a top-level Request object, this extension limits the number
    of VMs from one experiment that Emulab will collocate on each physical
    host.
    """
    _mfactor = None
    
    def __init__(self, mfactor):
        """mfactor is an integer, giving the maximum number of VMs to multiplex
        on each physical host."""
        if setCollocateFactor._mfactor:
            raise EmulabExtensionDuplicateStatement("setCollocateFactor")
        self.mfactor = setCollocateFactor._mfactor = mfactor
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}collocate_factor" % (Namespaces.EMULAB.name))
        el.attrib["count"] = str(self.mfactor)
        return root

Request.EXTENSIONS.append(("setCollocateFactor", setCollocateFactor))

class setPackingStrategy(object):
    """Added to a top-level Request object, this extension controls the
    strategy used for distributing VMs across physical hosts
    """

    _strategy = None
    
    def __init__(self, strategy):
        if setPackingStrategy._strategy:
            raise EmulabExtensionDuplicateStatement("setPackingStrategy")
        self.strategy = setPackingStrategy._strategy = strategy
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}packing_strategy" % (Namespaces.EMULAB.name))
        el.attrib["strategy"] = str(self.strategy)
        return root

Request.EXTENSIONS.append(("setPackingStrategy", setPackingStrategy))
    
class setRoutingStyle(object):
    """Added to a top-level Request object, this extension controls the
    routing that is automatically configured on the experiment (data-plane)
    side of the network.
    """
    _style = None
    
    def __init__(self, style):
        if setRoutingStyle._style:
            raise EmulabExtensionDuplicateStatement("setRoutingStyle")
        self.style = setRoutingStyle._style = style;
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}routing_style" % (Namespaces.EMULAB.name))
        el.attrib["style"] = str(self.style)
        return root

Request.EXTENSIONS.append(("setRoutingStyle", setRoutingStyle))

class setDelayImage(object):
    """Added to a top-level Request object, this extension sets the disk image
    that will be used for all delay nodes configured for the experiment.
    """
    _urn = None
    
    def __init__(self, urn):
        """urn: URN of any image - to perform the intnded function, the 
        image must be capable of setting up bridging and/or traffic shaping.
        """
        if setDelayImage._urn:
            raise EmulabExtensionDuplicateStatement("setDelayImage")
        self.urn = setDelayImage._urn = urn
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}delay_image" % (Namespaces.EMULAB.name))
        el.attrib["urn"] = str(self.urn)
        return root

Request.EXTENSIONS.append(("setDelayImage", setDelayImage))

class setForceShaping(object):
    """Added to a Link or LAN object, this extension forces Emulab link
    shaping to be enabled, even if it is not strictly necessary. This
    allows the link properties to be changed dynamically via the Emulab event
    system.
    """
    _enabled = False
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}force_shaping" % (Namespaces.EMULAB.name))
        el.attrib["enabled"] = "true"
        return root

Link.EXTENSIONS.append(("setForceShaping", setForceShaping))

class setUseTypeDefaultImage(object):
    """Added to a node that does not specify a disk image, this extension
    forces Emulab to use the hardware type default image instead of the
    standard geni default image. Useful with special hardware that should
    run a special image.
    """
    _enabled = False
    
    def __init__(self):
        self._enabled = True
    
    def _write(self, root):
        if self._enabled == False:
            return root
        el = ET.SubElement(root, "{%s}use_type_default_image"
                           % (Namespaces.EMULAB.name))
        el.attrib["enabled"] = "true"
        return root

Node.EXTENSIONS.append(("setUseTypeDefaultImage", setUseTypeDefaultImage))

#
# Emulab Program Agents.
#
class ProgramAgent(Service):
    """Add an Emulab Program Agent, which can be controlled via the Emulab
    event system. Optional argument 'directory' specifies where to invoke
    the command from. Optional argument 'onexpstart' says to invoke the
    command when the experiment starts (time=0 in event speak). This is
    different than the Execute service, which runs every time the node boots.
    """
    def __init__ (self, name, command, directory = None, onexpstart = False):
        super(ProgramAgent, self).__init__()
        self.name = name
        self.command = command
        self.directory = directory
        self.onexpstart = onexpstart

    def _write (self, element):
        exc = ET.SubElement(element,
                            "{%s}program-agent" % (Namespaces.EMULAB.name))
        exc.attrib["name"] = self.name
        if isinstance(self.command, Command):
            exc.attrib["command"] = self.command.resolve()
        else:
            exc.attrib["command"] = self.command
            pass
        if self.directory:
            exc.attrib["directory"] = self.directory
            pass
        if self.onexpstart:
            exc.attrib["onexpstart"] = "true"
            pass
        return exc
