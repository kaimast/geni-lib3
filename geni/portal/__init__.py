# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

import sys
import os
import atexit
import warnings
import json
import optparse

class ParameterType (object):
  INTEGER     = "integer"
  STRING      = "string"
  BOOLEAN     = "boolean"
  IMAGE       = "image"
  AGGREGATE   = "aggregate"
  NODETYPE    = "nodetype"

class Context (object):

  def __init__ (self):
    self._parameters = {}
    self._bindingDone = False
    if 'GENILIB_PORTAL_MODE' in os.environ:
      self._standalone = False
      self._portalRequestPath = os.environ['GENILIB_PORTAL_REQUEST_PATH']
      self._dumpParamsPath = os.environ.get('GENILIB_PORTAL_DUMPPARAMS_PATH',None)
    else:
      self._standalone = True
      self._portalRequestPath = None

  def printRequestRSpec (self, rspec):
    rspec.writeXML(self._portalRequestPath)

  def defineParameter (self, name, description, type, defaultValue, legalValues = None):
    # TODO: Duplicate checking
    self._parameters[name] = {'description': description, 'type': type,
        'defaultValue': defaultValue, 'legalValues': legalValues}
    if len(self._parameters) == 1:
      atexit.register(self._checkBind)

  def bindParameters(self):
    self._bindingDone = True
    if self._standalone:
      return self._bindParametersCmdline()
    else:
      if self._dumpParamsPath:
        self._dumpParamsJSON()
        sys.exit(0)
      else:
        return self._bindParametersEnv()

  def _bindParametersCmdline (self):
    parser = optparse.OptionParser()
    for name, opts in self._parameters.iteritems():
      # TODO: handle different types of parameters correctly
      parser.add_option("--" + name, action="store", dest=name, default=opts['defaultValue'], help=opts['description'])
    return parser.parse_args()

  def _bindParametersEnv (self):
    # TODO: Implement
    return {}

  def _dumpParamsJSON (self):
    f = open(self._dumpParamsPath, "w+")
    json.dump(self._parameters,f)
    return

  def _checkBind (self):
    if len(self._parameters) > 0 and not self._bindingDone:
      warnings.warn("Parameters were defined, but never bound with bindParameters()", RuntimeWarning)
