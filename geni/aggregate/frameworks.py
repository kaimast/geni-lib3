# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os.path

#from cryptography import x509
#from cryptography.hazmat.backends import default_backend

from .core import FrameworkRegistry
from .. import tempfile

class KeyDecryptionError(Exception): pass

class ClearinghouseError(Exception):
  def __init__ (self, text, data = None):
    super(ClearinghouseError, self).__init__()
    self.text = text
    self.data = data
  def __str__ (self):
    return self.text


class Project(object):
  def __init__ (self):
    self.expired = None
    self.urn = None

class CHAPI2Project(Project):
  def __init__ (self, pinfo):
    super(CHAPI2Project, self).__init__()


class Member(object):
  def __init__ (self):
    self.urn = None
    self.uid = None
    self.emulab_role = None
    self.roles = {}

  @property
  def shortname (self):
    return self.urn.split("+")[-1]

  def _set_from_project (self, project_info):
    self.urn = project_info["PROJECT_MEMBER"]
    self.roles[project_info["PROJECT_URN"]] = project_info["PROJECT_ROLE"]

    try:
      self.uid = project_info["PROJECT_MEMBER_UID"]
    except KeyError:
      pass

    try:
      self.emulab_role = project_info["PROJECT_EMULAB_ROLE"]
    except KeyError:
     pass


class _MemberRegistry(object):
  def __init__ (self):
    self._members = {}

  def addProjectInfo (self, project_info):
    try:
      m = self._members[project_info["PROJECT_MEMBER"]]
    except KeyError:
      m = Member()
      self._members[project_info["PROJECT_MEMBER"]] = m

    m._set_from_project(project_info)
    return m


MemberRegistry = _MemberRegistry()

class Framework(object):
  class KeyPathError(Exception):
    def __init__ (self, path):
      super(Framework.KeyPathError, self).__init__()
      self.path = path
    def __str__ (self):
      return "Path %s does not contain a key" % (self.path)

  def __init__ (self, name = None):
    self.name = name
    self._type = None
    self._authority = None
    self._ch = None
    self._ma = None
    self._sa = None
    self._cert = None
    self._key = None
    self._project = None
    self._userurn = None

  @property
  def project (self):
    return self._project

  @project.setter
  def project (self, val):
    self._project = val

  @property
  def projecturn (self):
    # TODO:  Exception
    return None

  @property
  def key (self):
    return self._key

  @key.setter
  def key (self, path):
    self._key = path

  def setKey (self, path, passwd):
    if not os.path.exists(path):
      raise Framework.KeyPathError(path)
    (tf, dpath) = tempfile.makeFile()

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    try:
      key = serialization.load_pem_private_key(open(path, "rb").read(), passwd, default_backend())
    except ValueError:
      raise KeyDecryptionError()

    data = key.private_bytes(serialization.Encoding.PEM,
                             serialization.PrivateFormat.TraditionalOpenSSL,
                             serialization.NoEncryption())
    tf.write(data)
    tf.close()

    self._key = dpath

  @property
  def cert (self):
    return self._cert

  @cert.setter
  def cert (self, val):
    self._cert = val

  @property
  def userurn (self):
    if not self._userurn:
      from cryptography import x509
      from cryptography.hazmat.backends import default_backend
      cert = x509.load_pem_x509_certificate(open(self._cert, "rb").read(), default_backend())
      for ext in cert.extensions:
        if ext.oid == x509.SubjectAlternativeName.oid:
          for uri in ext.value.get_values_for_type(x509.UniformResourceIdentifier):
            if uri.startswith("urn:publicid"):
              self._userurn = uri
              break
    return self._userurn


class ProtoGENI(Framework):
  def __init__ (self, name = "pg"):
    super(ProtoGENI, self).__init__(name)
    self._type = "pgch"


class Emulab(ProtoGENI):
  SA = "https://www.emulab.net:12369/protogeni/xmlrpc/project/%s/sa"
  MA = "https://www.emulab.net:12369/protogeni/xmlrpc/project/%s/ma"

  def __init__ (self):
    super(Emulab, self).__init__("emulab")
    self._type = "pgch"
    self._ch = "https://www.emulab.net:443/protogeni/xmlrpc/ch"
    self._sa = None
    self._ma = None

  @property
  def project (self):
    return super(Emulab, self).project

  @project.setter
  def project (self, val):
    super(Emulab, self).project.fset(self, val)
    self._sa = Emulab.SA % (val)
    self._ma = Emulab.MA % (val)


class CHAPI1(Framework):
  def __init__ (self, name = "chapi"):
    super(CHAPI1, self).__init__(name)
    self._type = "chapi"


class CHAPI2(Framework):
  def __init__ (self, name = "chapi"):
    super(CHAPI2, self).__init__(name)
    self._type = "chapi"

  def projectNameToURN (self, name):
    ### TODO: Exception
    return None

  def sliceNameToURN (self, slice_name, project = None):
    ### TODO: Exception
    return None

  def createProject (self, context, name, exp, desc):
    from ..minigcf import chapi2

    res = chapi2.create_project(self._sa, False, self.cert, self.key, [context.ucred_api3], name, exp, desc)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listProjectMembers (self, context, project_urn = None):
    if not project_urn:
      project_urn = self.projecturn

    from ..minigcf import chapi2
    res = chapi2.lookup_project_members(self._sa, False, self.cert, self.key, [context.ucred_api3], project_urn)
    if res["code"] == 0:
      members = []
      for mobj in res["value"]:
        mobj["PROJECT_URN"] = project_urn
        members.append(MemberRegistry.addProjectInfo(mobj))
      return members
    else:
      raise ClearinghouseError(res["output"], res)

  def listProjects (self, context, own = True):
    from ..minigcf import chapi2

    if not own:
      res = chapi2.lookup_projects(self._sa, False, self.cert, self.key, [context.ucred_api3])
    else:
      res = chapi2.lookup_projects_for_member(self._sa, False, self.cert, self.key,
                                              [context.ucred_api3], context.userurn)

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listAggregates (self, context):
    from ..minigcf import chapi2

    res = chapi2.lookup_aggregates(self._ch, False, self.cert, self.key)

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listSlices (self, context):
    from ..minigcf import chapi2
    res = chapi2.lookup_slices_for_project(self._sa, False, self.cert, self.key,
                                           [context.ucred_api3], context.project_urn)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listSliceMembers (self, context, slicename):
    from ..minigcf import chapi2

    slice_urn = self.sliceNameToURN(slicename)

    res = chapi2.lookup_slice_members(self._sa, False, self.cert, self.key,
                                      [context.ucred_api3], slice_urn)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def addSliceMembers (self, context, slicename, members, role = None):
    from ..minigcf import chapi2

    if not role:
      role = chapi2.SLICE_ROLE.MEMBER

    if not isinstance(members, (list,set,tuple)):
      members = [members]

    slice_urn = self.sliceNameToURN(slicename)
    
    res = chapi2.modify_slice_membership(self._sa, False, self.cert, self.key, [context.ucred_api3],
                                         slice_urn, add = [(x.urn, role) for x in members])

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def removeSliceMembers (self, context, slicename, members):
    from ..minigcf import chapi2

    if not isinstance(members, (list,set,tuple)):
      members = [members]

    slice_urn = self.sliceNameToURN(slicename)
    
    res = chapi2.modify_slice_membership(self._sa, False, self.cert, self.key, [context.ucred_api3],
                                         slice_urn, remove = [x.urn for x in members])

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def getUserCredentials (self, owner_urn):
    from ..minigcf import chapi2
    res = chapi2.get_credentials(self._ma, False, self.cert, self.key, [], owner_urn)
    if res["code"] == 0:
      return res["value"][0]["geni_value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def getSliceCredentials (self, context, slicename):
    from ..minigcf import chapi2

    slice_urn = self.sliceNameToURN(slicename)

    res = chapi2.get_credentials(self._sa, False, self.cert, self.key, [context.ucred_api3], slice_urn)
    if res["code"] == 0:
      return res["value"][0]["geni_value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def createSlice (self, context, slicename, project_urn = None, exp = None, desc = None):
    from ..minigcf import chapi2

    if project_urn is None:
      project_urn = self.projectNameToURN(context.project)

    res = chapi2.create_slice(self._sa, False, self.cert, self.key, [context.ucred_api3], slicename, project_urn, exp, desc)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def renewSlice (self, context, slicename, exp):
    from ..minigcf import chapi2

    fields = {"SLICE_EXPIRATION" : exp.strftime(chapi2.DATE_FMT)}
    slice_urn = self.sliceNameToURN(slicename)
    slice_info = context.getSliceInfo(slicename)

    res = chapi2.update_slice(self._sa, False, self.cert, self.key,
                              [slice_info.cred_api3, context.ucred_api3],
                              slice_urn, fields)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def lookupSSHKeys (self, context, user_urn):
    from ..minigcf import chapi2

    res = chapi2.lookup_key_info(self._ma, False, self.cert, self.key, [context.ucred_api3], user_urn)
    if res["code"] == 0:
      key_list = [x["KEY_PUBLIC"] for x in res["value"].values()]
      return key_list
    else:
      raise ClearinghouseError(res["output"], res)


class Portal(CHAPI2):
  def __init__ (self):
    super(Portal, self).__init__("gpo-ch2")
    self._authority = "ch.geni.net"
    self._ch = "https://ch.geni.net:8444/CH"
    self._ma = "https://ch.geni.net:443/MA"
    self._sa = "https://ch.geni.net:443/SA"

  @property
  def projecturn (self):
    return self.projectNameToURN(self.project)

  def projectNameToURN (self, name):
    return "urn:publicid:IDN+ch.geni.net+project+%s" % (name)

  def sliceNameToURN (self, name, project = None):
    if not project:
      project = self.project
    return "urn:publicid:IDN+ch.geni.net:%s+slice+%s" % (project, name)


class EmulabCH2(CHAPI2):
  SA = "https://www.emulab.net:12369/protogeni/xmlrpc/geni-sa/2"
#  SA = "https://www.emulab.net:12369/protogeni/xmlrpc/project/%s/geni-sa/2"
  MA = "https://www.emulab.net:12369/protogeni/xmlrpc/geni-ma"
#  MA = "https://www.emulab.net:12369/protogeni/xmlrpc/project/%s/geni-ma"

  def __init__ (self):
    super(EmulabCH2, self).__init__("emulab-ch2")
    self._authority = ""
    self._ch = None
    self._sa = None
    self._ma = None

  @property
  def projecturn (self):
    return self.projectNameToURN(self.project)

  def projectNameToURN (self, name):
    return "urn:publicid:IDN+emulab.net+project+%s" % (name)

  def sliceNameToURN (self, name, project = None):
    if not project:
      project = self.project
    return "urn:publicid:IDN+emulab.net:%s+slice+%s" % (project, name)

  @property
  def project (self):
    return super(EmulabCH2, self).project

  @project.setter
  def project (self, val):
    self._project = val
    self._sa = EmulabCH2.SA
    self._ma = EmulabCH2.MA
#    self._ma = EmulabCH2.MA % (val)

#  def listSlices (self, context):
#    from ..minigcf import chapi2
#    res = chapi2._lookup(self._sa, False, self.cert, self.key, "SLICE", [context.ucred_api3], {})
#    if res["code"] == 0:
#      return res["value"]
#    else:
#      raise ClearinghouseError(res["output"], res)

FrameworkRegistry.register("portal", Portal)
FrameworkRegistry.register("gpo-ch2", Portal)
FrameworkRegistry.register("pg", ProtoGENI)
FrameworkRegistry.register("emulab-ch2", EmulabCH2)
