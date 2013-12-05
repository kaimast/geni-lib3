# Copyright (c) 2013  Barnstormer Softworks, Ltd.

class Namespace(object):
  def __init__ (self, prefix, name, location = None):
    self.prefix = prefix
    self.name = name
    self.location = location

XSNS = Namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

REQUEST = Namespace("request", "http://www.geni.net/resource/rspec/3", "http://www.geni.net/resources/rspec/3/request.xsd")
OFv3 = Namespace("openflow", "http://www.geni.net/resources/rspec/ext/openflow/3")
OFv4 = Namespace("openflow", "http://www.geni.net/resources/rspec/ext/openflow/4")
SVLAN = Namespace("sharedvlan", "http://www.geni.net/resources/rspec/ext/shared-vlan/1", "http://www.geni.net/resources/rspec/ext/shared-vlan/1/request.xsd")

