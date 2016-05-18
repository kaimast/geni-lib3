from __future__ import absolute_import

from ..pg import RawPC
from .pndefs import PNDEFS

class eNodeB(RawPC):
    _ENODEB_OS = "GENERICDEV-NOVLANS"

    def __init__ (self, client_id, component_id = None):
        super(eNodeB, self).__init__(client_id, component_id = component_id)
        self.hardware_type = "enodeb"  # set hwtype to general eNB node class.
        self.disk_image = PNDEFS.SYSTEMIMG_URN_PREFIX + eNodeB._ENODEB_OS
