# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

import sys
import os
import atexit
import warnings
import json
import argparse

class ParameterType (object):
  INTEGER     = "integer"
  STRING      = "string"
  BOOLEAN     = "boolean"
  IMAGE       = "image"
  AGGREGATE   = "aggregate"
  NODETYPE    = "nodetype"

  argparsemap = { INTEGER: int, STRING: str, BOOLEAN: bool, IMAGE: str,
                  AGGREGATE: str, NODETYPE: str }

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
    parser = argparse.ArgumentParser()
    for name, opts in self._parameters.iteritems():
      parser.add_argument("--" + name,
                          type    = ParameterType.argparsemap[opts['type']],
                          default = opts['defaultValue'],
                          choices = opts['legalValues'],
                          help    = opts['description'])
    return vars(parser.parse_args())

  def _bindParametersEnv (self):
    params = {}
    for name, opts in self._parameters.iteritems():
      val = os.environ.get("GENILIB_PORTAL_ARG_%s" % name, opts['defaultValue'])
      if opts['legalValues'] and val not in opts['legalValues']:
        # TODO: Not 100% sure what the right thing is to do here, need to get 
        # the error back in a nice machine-parsable form
        sys.stderr.write("ERROR: Illegal value '%s' for option '%s'\n" %
            (val, name))
        sys.exit(1)
      params[name] = ParameterType.argparsemap[opts['type']](val)
    return params

  def _dumpParamsJSON (self):
    f = open(self._dumpParamsPath, "w+")
    json.dump(self._parameters,f)
    return

  def _checkBind (self):
    if len(self._parameters) > 0 and not self._bindingDone:
      warnings.warn("Parameters were defined, but never bound with bindParameters()", RuntimeWarning)
