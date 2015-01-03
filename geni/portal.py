# Copyright (c) 2014 The University of Utah

from __future__ import absolute_import

import sys
import os
import atexit
import warnings
import json
import argparse
from argparse import Namespace

class ParameterType (object):
  """Parameter types understood by Context.defineParameter()."""

  INTEGER     = "integer"
  STRING      = "string"
  BOOLEAN     = "boolean"
  IMAGE       = "image"
  AGGREGATE   = "aggregate"
  NODETYPE    = "nodetype"
  BANDWIDTH   = "bandwidth"
  LATENCY     = "latency"
  SIZE        = "size"

  argparsemap = { INTEGER: int, STRING: str, BOOLEAN: bool, IMAGE: str,
                  AGGREGATE: str, NODETYPE: str }

class Context (object):
  """Handle context for scripts being run inside a portal.

  This class handles context for the portal, including where to put output
  RSpecs and handling parameterized scripts.

  Scripts using this class can also be run "standalone" (ie. not by the
  portal), in which case they take parameters on the command line and put
  RSpecs on the standard output."""

  def __init__ (self):
    self._parameters = {}
    self._bindingDone = False
    if 'GENILIB_PORTAL_MODE' in os.environ:
      self._standalone = False
      self._portalRequestPath = os.environ.get('GENILIB_PORTAL_REQUEST_PATH',None)
      self._dumpParamsPath = os.environ.get('GENILIB_PORTAL_DUMPPARAMS_PATH',None)
      self._readParamsPath = os.environ.get('GENILIB_PORTAL_PARAMS_PATH',None)
    else:
      self._standalone = True
      self._portalRequestPath = None

  def printRequestRSpec (self, rspec):
    """Print the given request RSpec.
    
    If run standalone (not in the portal), the request will be printed to the
    standard output; if run in the portal, it will be placed someplace the
    portal can pick it up."""
    rspec.writeXML(self._portalRequestPath)

  def defineParameter (self, name, description, type, defaultValue,
      legalValues = None):
    """Define a new paramter to the script.

    The given name will be used when parameters are bound. The description is
    help text that will be shown to the user when making his/her selection/ The
    type should be one of the types defined by ParameterType. defaultValue is
    required, but legalValues (a list) is optional; the defaultValue must be
    one of the legalValues.
    
    After defining parameters, bindParameters() must be called exactly once."""
    self._parameters[name] = {'description': description, 'type': type,
        'defaultValue': defaultValue, 'legalValues': legalValues}
    if len(self._parameters) == 1:
      atexit.register(self._checkBind)

  def bindParameters (self):
    """Returns values for the parameters defined by defineParameter().
    
    Returns a Namespace (like argparse), so if you call foo = bindParameters(), a
    parameter defined with name "bar" is accessed as foo.bar . Since defaults
    are required, all parameters are guaranteed to have values in the Namespace

    If run standaline (not in the portal), parameters are pulled from the command
    line (try running with --help); if run in the portal, they are pulled from
    the portal itself."""
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
    return parser.parse_args()

  def _bindParametersEnv (self):
    namespace = Namespace()
    paramValues= {}
    if self._readParamsPath:
        f = open(self._readParamsPath, "r")
        paramValues = json.load(f)
        f.close()
    for name, opts in self._parameters.iteritems():
      val = paramValues.get(name, opts['defaultValue'])
      if opts['legalValues'] and val not in opts['legalValues']:
        # TODO: Not 100% sure what the right thing is to do here, need to get 
        # the error back in a nice machine-parsable form
        sys.exit("ERROR: Illegal value '%s' for option '%s'" % (val, name))
      setattr(namespace, name, ParameterType.argparsemap[opts['type']](val))
    return namespace

  def _dumpParamsJSON (self):
    f = open(self._dumpParamsPath, "w+")
    json.dump(self._parameters,f)
    f.close()
    return

  def _checkBind (self):
    if len(self._parameters) > 0 and not self._bindingDone:
      warnings.warn("Parameters were defined, but never bound with " +
          " bindParameters()", RuntimeWarning)
