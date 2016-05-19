from __future__ import absolute_import

from ..pg import Link

#
# Class to hide the idiosynchrasies of PhantomNet RF links.
#
class RFLink(Link):
    def __init__(self, name):
        super(RFLink, self).__init__(name)
        self.bandwidth = 500
  
    def _write(self, root):
        lnk = super(RFLink, self)._write(root)
        lnk.attrib["protocol"] = "P2PLTE"
        return lnk
