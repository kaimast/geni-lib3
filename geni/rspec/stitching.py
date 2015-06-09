# Copyright (c) 2015  Barnstormer Softworks, Ltd.

from __future__ import absolute_import

import datetime

from . import pg
from .. import namespaces

STITCHNS = Namespace("stitch", "http://hpn.east.isi.edu/rspec/ext/stitch/0.1/")

class StitchInfo(pg.Resource):
  def __init__ (self):
    self._paths = []

  def addPath (self, path):
    self._paths.append(path)
    return path

  def _write (self, element):
    se = ET.SubElement(element, "{%s}stitching" % (STITCHNS))
    se.attrib["lastUpdateTime"] = datetime.datetime.now().strftime("%Y%m%d:%H:%M:%S")

    for path in self._paths:
      path._write(se)


class Path(object):
  def __init__ (self, name):
    self.name = name
    self._hops = []

  def addHop (self, hop):
    self._hops.append(hop)
    return hop

  def _write (self, element):
    pe = ET.SubElement(element, "{%s}path" % (STITCHNS))
    pe.attrib["id"] = self.name

    # We wait until writing to give them IDs, so you can do all kinds of stupid things
    # like reordering and deleting until then
    for idx,hop in enumerate(self._hops, start=1):
      hop._id = idx
      if len(self._hops) == idx:
        hop._next_hop_id = None

    for hop in self._hops:
      hop._write(pe)

    return pe


class Hop(object):
  def __init__ (self):
    self.link_id = None
    self.capacity = 1
    self.suggested_vlan = None
    self._id = None
    self._next_hop_id = None

    # Don't override these unless the aggregate hates you
    self.ad_vrange_low = 1
    self.ad_vrange_high = 4092
    self.vlan_translation = False

  def _write (self, element):
    he = ET.SubElement(element, "{%s}hop" % (STITCHNS))
    he.attrib["id"] = "%d" % (self._id)

    link = ET.SubElement(he, "{%s}link" % (STITCHNS))
    link.attrib["id"] = self.link_id

    tem = ET.SubElement(link, "{%s}trafficEngineeringMetric" % (STITCHNS))
    tem.text = "10"

    ce = ET.SubElement(link, "{%s}capacity" % (STITCHNS))
    ce.text = "%d" % (self.capacity)

    scd = ET.SubElement(link, "{%s}switchingCapabilityDescriptor" % (STITCHNS))
    
    sct = ET.SubElement(scd, "{%s}switchingcapType" % (STITCHNS))
    sct.text = "l2sc"

    enc = ET.SubElement(scd, "{%s}encodingType" % (STITCHNS))
    enc.text = "ethernet"

    scs = ET.SubElement(scd, "{%s}switchingCapabilitySpecificInfo" % (STITCHNS))
    l2scs = ET.SubElement(scs, "{%s}switchingCapabilitySpecificInfo_L2sc" % (STITCHNS))

    imtu = ET.SubElement(l2scs, "{%s}interfaceMTU" % (STITCHNS))
    imtu = "1500"

    vra = ET.SubElement(l2scs, "{%s}vlanRangeAvailability" % (STITCHNS))
    vra.text = "%d-%d" % (self.ad_vrange_low, self.ad_vrange_high)

    svr = ET.SubElement(l2scs, "{%s}suggestedVLANRange" % (STITCHNS))
    svr.text = "%d" % (self.suggested_vlan)

    vt = ET.SubElement(l2scs, "{%s}vlanTranslation" % (STITCHNS))
    vt.text = str(vlan_translation).lower()

    nh = ET.SubElement(he, "{%s}nextHop" % (STITCHNS))
    if self._next_hop_id:
      nh.text = "%d" % (self._next_hop_id)
    else:
      nh.text = "null"

    return he
