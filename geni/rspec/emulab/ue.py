from __future__ import absolute_import

from ..pg import RawPC
from .pndefs import PNDEFS

class UE(RawPC):
    def __init__ (self, client_id, component_id = None):
        super(UE, self).__init__(client_id, component_id = component_id)
        self.hardware_type = "ue"
