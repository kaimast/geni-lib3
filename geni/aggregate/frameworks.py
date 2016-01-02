# Copyright (c) 2014-2015  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import subprocess
import os.path

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
    self.roles = {}

  def _set_from_project (self, project_info):
    self.urn = project_info["PROJECT_MEMBER"]
    self.uid = project_info["PROJECT_MEMBER_UID"]
    self.roles[project_info["PROJECT_URN"]] = project_info["PROJECT_ROLE"]

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

  @property
  def key (self):
    return self._key

  @key.setter
  def key (self, val):
    if not os.path.exists(val):
      raise Framework.KeyPathError(val)
    (tf, path) = tempfile.makeFile()
    tf.close()
    ### TODO: WARN IF OPENSSL IS NOT PRESENT
    ### TODO: Make ssl binary paths configurable
    if os.name == "nt":
      nullf = open("NUL")
      binp = os.path.normpath("C:/OpenSSL-Win32/bin/openssl")
      ret = subprocess.call("%s rsa -in \"%s\" -out \"%s\"" % (binp, val, path), stdout=nullf, stderr=nullf, shell=True)
      self._key = path
    else:
      nullf = open("/dev/null")
      # We really don't want shell=True here, but there are pty problems with openssl otherwise
      ret = subprocess.call("/usr/bin/openssl rsa -in %s -out %s" % (val, path), stdout=nullf, stderr=nullf, shell=True)
      # TODO: Test the size afterwards to make sure the password was right, or parse stderr?
      self._key = path

  def setKey (self, path, passwd):
    if not os.path.exists(path):
      raise Framework.KeyPathError(path)
    (tf, dpath) = tempfile.makeFile()

    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization

    try:
      key = serialization.load_pem_private_key(open(path, "rb").read(), passwd, default_backend())
    except ValueError, e:
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

  def _update (self, context):
    pass


class ProtoGENI(Framework):
  def __init__ (self, name = "pg"):
    super(ProtoGENI, self).__init__(name)
    self._type = "pgch"


class Emulab(ProtoGENI):
  def __init__ (self):
    super(Emulab, self).__init__("emulab")
    self._type = "pgch"
    self._ch = "https://www.emulab.net:443/protogeni/xmlrpc/ch"
    self._ca = "https://www.emulab.net:443/protogeni/xmlrpc/sa"


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

  def sliceNameToURN (self, project, name):
    ### TODO: Exception
    return None

  def listProjectMembers (self, context, project_urn = None):
    if not project_urn:
      project_urn = self.projectNameToURN(context.project)

    from ..minigcf import chapi2
    ucred = open(context.usercred_path, "r").read()
    res = chapi2.lookup_project_members(self._sa, False, self.cert, self.key, [ucred], project_urn)
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
    ucred = open(context.usercred_path, "r").read()

    if not own:
      res = chapi2.lookup_projects(self._sa, False, self.cert, self.key, [ucred])
    else:
      res = chapi2.lookup_projects_for_member(self._sa, False, self.cert, self.key, [ucred], context.userurn)

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listAggregates (self, context):
    from ..minigcf import chapi2
    ucred = open(context.usercred_path, "r").read()

    res = chapi2.lookup_aggregates(self._ch, False, self.cert, self.key)

    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def listSlices (self, context):
    from ..minigcf import chapi2
    ucred = open(context.usercred_path, "r").read()
    return chapi2.lookup_slices_for_project (self._sa, False, self.cert, self.key, [ucred], context.project_urn)

  def getUserCredentials (self, owner_urn):
    from ..minigcf import chapi2
    res = chapi2.get_credentials(self._ma, False, self.cert, self.key, [], owner_urn)
    if res["code"] == 0:
      return res["value"][0]["geni_value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def getSliceCredentials (self, context, slicename):
    from ..minigcf import chapi2

    ucred = open(context.usercred_path, "r").read()
    slice_urn = self.sliceNameToURN(context.project, slicename)

    res = chapi2.get_credentials(self._sa, False, self.cert, self.key, [ucred], slice_urn)
    if res["code"] == 0:
      return res["value"][0]["geni_value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def createSlice (self, context, slicename, project_urn = None, exp = None, desc = None):
    from ..minigcf import chapi2
    ucred = open(context.usercred_path, "r").read()

    if project_urn is None:
      project_urn = self.projectNameToURN(context.project)

    res = chapi2.create_slice(self._sa, False, self.cert, self.key, [ucred], slicename, project_urn, exp, desc)
    if res["code"] == 0:
      return res["value"]
    else:
      raise ClearinghouseError(res["output"], res)

  def renewSlice (self, context, slicename, exp):
    from ..minigcf import chapi2
    ucred = open(context.usercred_path, "r").read()

    fields = {"SLICE_EXPIRATION" : exp.strftime(chapi2.DATE_FMT)}
    slice_urn = self.sliceNameToURN(context.project, slicename)

    ret = chapi2.update_slice(self._sa, False, self.cert, self.key, [ucred], slice_urn, fields)
    return ret


class Portal(CHAPI2):
  def __init__ (self):
    super(Portal, self).__init__("portal")
    self._authority = "ch.geni.net"
    self._ch = "https://ch.geni.net:8444/CH"
    self._ma = "https://ch.geni.net:443/MA"
    self._sa = "https://ch.geni.net:443/SA"

  def projectNameToURN (self, name):
    return "urn:publicid:IDN+ch.geni.net+project+%s" % (name)

  def sliceNameToURN (self, project, name):
    return "urn:publicid:IDN+ch.geni.net:%s+slice+%s" % (project, name)

  def getConfig (self):
    l = []
    l.append("[%s]" % (self.name))
    l.append("type = %s" % (self._type))
    l.append("authority = %s" % (self._authority))
    l.append("ch = %s" % (self._ch))
    l.append("sa = %s" % (self._sa))
    l.append("ma = %s" % (self._ma))
    l.append("cert = %s" % (self.cert))
    l.append("key = %s" % (self.key))
    return l


class EmulabCH2(CHAPI1):
  def __init__ (self):
    super(EmulabCH2, self).__init__("emulab-ch2")
    self._authority = ""
    self._ch = "https://www.emulab.net:12370/protogeni/pubxmlrpc/sr"
    self._ma = "https://www.emulab.net:12369/protogeni/xmlrpc/geni-ma"
    self._sa = "https://www.emulab.net:12369/protogeni/xmlrpc/geni-sa"

FrameworkRegistry.register("portal", Portal)
FrameworkRegistry.register("pg", ProtoGENI)
FrameworkRegistry.register("emulab-ch2", EmulabCH2)
