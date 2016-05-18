#
# Static set of EPC roles
#
class EPCROLES(object):
    ANY          = "any"
    ENABLERS     = "epc-enablers"
    PGW          = "pgw"
    SGW_MME_SGSN = "sgw-mme-sgsn"
    CLIENT       = "epc-client"
    ENODEB       = "enodeb"

#
# Static set of EPC lans (recognized by PhantomNet setup code)
#
class EPCLANS(object):
    MGMT   = "mgmt"
    NET_A  = "net-a"
    NET_B  = "net-b"
    NET_C  = "net-c"
    NET_D  = "net-d"
    AN_LTE = "an-lte"

#
# Other global constants
#
class PNDEFS(object):
    PNETIMG_URN_PREFIX = "urn:publicid:IDN+emulab.net+image+PhantomNet:"
    SYSTEMIMG_URN_PREFIX = "urn:publicid:IDN+emulab.net+image+emulab-ops:"
    DEF_BINOEPC_IMG = PNETIMG_URN_PREFIX + "UBUNTU12-64-BINOEPC"
