from __future__ import absolute_import

from ..pg import RawPC, Execute, Request
from ..igext import XenVM
from .epcexc import InvalidRole, InvalidRequestRSpec, UnboundRSpec
from .pndefs import EPCROLES, EPCLANS, PNDEFS
from .epclan import EPClan

#
# Defaults used below
#
class _EPCDEFS(object):
    OEPC_STARTSCRIPT = "/opt/OpenEPC/bin/start_epc.sh"
    SUDOBIN = "/usr/bin/sudo"
    VM_RAM = 1024
    VALID_ROLES = (EPCROLES.ANY, EPCROLES.ENABLERS, EPCROLES.PGW, 
                   EPCROLES.SGW_MME_SGSN, EPCROLES.CLIENT, EPCROLES.ENODEB)

#
# Base EPC mixin node class.  This is the bulk of the implementation for
# both physical and VM node classes.
#
class _EPCBaseNode(object):
    _hwtype = None
    _image = PNDEFS.PNETIMG_URN_PREFIX + PNDEFS.DEF_BINOEPC_IMG
    _rspec = None

    def __init__ (self, client_id, role, hname = None, component_id = None,
                  prehook = None, posthook = None):
        if not role in _EPCDEFS.VALID_ROLES:
            raise InvalidRole(role)
        if not self._rspec:
            raise UnboundRSpec()
        super(_EPCBaseNode, self).__init__(client_id, component_id = component_id)
        self.role = role
        self.hname = hname
        self.startscript = _EPCDEFS.OEPC_STARTSCRIPT
        self.prehook = prehook
        self.posthook = posthook
        self._rspec.addResource(self)
        EPClan.addToLAN(EPCLANS.MGMT, self)

    @classmethod
    def setHWType(klass, hwtype):
        klass._hwtype = hwtype

    @classmethod
    def setImage(klass, img):
        klass._image = img

    @classmethod
    def bindRSpec(klass, rspec):
        if type(rspec) != Request:
            raise InvalidRequestRSpec()
        klass._rspec = rspec

    def _write(self, root):
        if not self.hardware_type and self._hwtype:
            self.hardware_type = self._hwtype
        if not self.disk_image and self._image:
            self.disk_image = self._image
        startcmd = "%s %s -r %s" % (_EPCDEFS.SUDOBIN, self.startscript, 
                                    self.role)
        if self.hname:
            startcmd += " -h %s" % self.hname
        if self.prehook:
            startcmd += " -P %s" & self.prehook
        if self.posthook:
            startcmd += " -T %s" & self.posthook
        self.addService(Execute(shell="csh", command=startcmd))
        return super(_EPCBaseNode, self)._write(root)


#
# Physical EPC node class
#
class EPCNode(_EPCBaseNode,RawPC):
    pass


#
# VM EPC node class
#
class EPCVMNode(_EPCBaseNode,XenVM):
    def __init__ (self, client_id, role, hname = None, component_id = None,
                  prehook = None, posthook = None):
        super(EPCVMNode, self).__init__(client_id, role, hname, component_id, 
                                        prehook, posthook)
        self.disk = 0 # No thin provisioning when set!
        self.ram = _EPCDEFS.VM_RAM
