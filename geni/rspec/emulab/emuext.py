# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Common set of RSpec extensions supported by many Emulab-based aggregates
"""

from __future__ import absolute_import

from ..pg import Request, Namespaces
from lxml import etree as ET

class EmulabExtensionDuplicateStatement(Exception):
    """This extension gets thrown if something that was only supposed to get
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
