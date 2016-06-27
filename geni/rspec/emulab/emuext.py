# Copyright (c) 2016 The University of Utah

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

from ..pg import Request, Namespaces
from lxml import etree as ET

class EmulabExtensionDuplicateStatement(Exception):
    def __init__ (self, classname):
        self._classname = classname

    def __str__ (self):
        return "%s may be used only once!" % str(self._classname,)

#
# Classs for icky emulab extension stuff, mostly to support existing
# NS file syntax.
#
class setCollocateFactor(object):
    _mfactor = None
    
    def __init__(self, mfactor):
        if setCollocateFactor._mfactor:
            raise EmulabExtensionDuplicateStatement("setCollocateFactor")
        self.mfactor = setCollocateFactor._mfactor = mfactor
    
    def _write(self, root):
        el = ET.SubElement(rspec,
                           "{%s}collocate_factor" % (Namespaces.EMULAB.name))
        el.attrib["count"] = str(self.mfactor)
        return root

Request.EXTENSIONS.append(("setCollocateFactor", setCollocateFactor))

class setPackingStrategy(object):
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
    _urn = None
    
    def __init__(self, urn):
        if setDelayImage._urn:
            raise EmulabExtensionDuplicateStatement("setDelayImage")
        self.urn = setDelayImage._urn = urn
    
    def _write(self, root):
        el = ET.SubElement(root,
                           "{%s}delay_image" % (Namespaces.EMULAB.name))
        el.attrib["urn"] = str(self.urn)
        return root

Request.EXTENSIONS.append(("setDelayImage", setDelayImage))
