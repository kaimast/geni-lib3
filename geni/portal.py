# Copyright (c) 2014-2015 The University of Utah
"""Library for dealing with scripts that are run in the context of a portal."""

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

  INTEGER     = "integer"       #: Simple integer
  STRING      = "string"        #: Any string
  BOOLEAN     = "boolean"       #: True/False
  IMAGE       = "image"         #: URN specifying a particular image
  AGGREGATE   = "aggregate"     #: URN specifying an Aggregate Manger
  NODETYPE    = "nodetype"      #: String specifying a type of node
  BANDWIDTH   = "bandwidth"     #: Floating-point number to be used for bandwidth
  LATENCY     = "latency"       #: Floating-point number to be used for latency
  SIZE        = "size"          #: Integer for size (eg. MB, GB, etc.)

  argparsemap = { INTEGER: int, STRING: str, BOOLEAN: bool, IMAGE: str,
                  AGGREGATE: str, NODETYPE: str, BANDWIDTH: float,
                  LATENCY: float, SIZE: int}

class Context (object):
  """Handle context for scripts being run inside a portal.

  This class handles context for the portal, including where to put output
  RSpecs and handling parameterized scripts.

  Scripts using this class can also be run "standalone" (ie. not by the
  portal), in which case they take parameters on the command line and put
  RSpecs on the standard output."""

  def __init__ (self):
    self._parameters = {}
    self._parameterGroups = {}
    self._parameterOrder = []
    self._parameterErrors = []
    self._parameterWarnings = []
    self._parameterWarningsAreFatal = False
    self._bindingDone = False
    if 'GENILIB_PORTAL_MODE' in os.environ:
      self._standalone = False
      self._portalRequestPath = os.environ.get('GENILIB_PORTAL_REQUEST_PATH',None)
      self._dumpParamsPath = os.environ.get('GENILIB_PORTAL_DUMPPARAMS_PATH',None)
      self._readParamsPath = os.environ.get('GENILIB_PORTAL_PARAMS_PATH',None)
      self._parameterWarningsAreFatal = \
        bool(os.environ.get('GENILIB_PORTAL_WARNINGS_ARE_FATAL',None))
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
      legalValues = None, longDescription = None, advanced = False,
      groupId = None):
    """Define a new paramter to the script.

    The given name will be used when parameters are bound. The description is
    brief help text that will be shown to the user when making his/her selection. The
    type should be one of the types defined by ParameterType. defaultValue is
    required, but legalValues (a list) is optional; the defaultValue must be
    one of the legalValues. Entries in the legalValues list may be either
    simple strings (eg. "m400"), in which case they will be show directly to
    the user, or 2-element tuples (eg. ("m400", "ARM64"),), in which the second
    entry is what is shown to the user. defaultValue may be a tuple, so that 
    one can pass, say, 'legalvalues[0]' for the option. The longDescription is
    an optional, detailed description of this parameter and how it relates to
    other parameters; it will be shown to the user if they ask to see the help,
    or as a pop-up/tooltip.  advanced, group, and groupName all provide parameter
    group abstractions.  Parameter groups are hidden by default from the user,
    and the user can expand them to view and modify them if desired.  By setting
    advanced to True, you create a parameter group named "Advanced Parameters";
    this group will not exist or be shown if none of your parameters set the
    'advanced' argument to True.
    
    After defining parameters, bindParameters() must be called exactly once."""

    if isinstance(defaultValue, tuple):
      defaultValue = defaultValue[0]

    if legalValues and defaultValue not in Context._legalList(legalValues):
      raise IllegalParameterDefaultError(defaultValue)

    self._parameterOrder.append(name)
    self._parameters[name] = {'description': description, 'type': type,
        'defaultValue': defaultValue, 'legalValues': legalValues,
        'longDescription': longDescription, 'advanced': advanced }
    if groupId is not None:
      self._parameters[name]['groupId'] = groupId
      pass
    if len(self._parameters) == 1:
      atexit.register(self._checkBind)

  def defineParameterGroup(self, groupId, groupName):
    """
    Define a parameter group.  Parameters may be added to this group, which has
    an identifying token composed of alphanumeric characters (groupId), and a
    human-readable name (groupName).  Groups are intended to be used for advanced
    parameters; in the portal UI, they hidden in an expandable panel with the
    groupName --- and the user can choose to see and modify them, or not.  You
    do not need to specify any groups; you can simply stuff all your parameters
    into the "Advanced Parameters" group by setting the 'advanced' argument of
    defineParameter to True.  If you need multiple groups, define your own
    groups this way.
    """
    self._parameterGroups[groupId] = groupName;
    pass

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

  def makeParameterWarningsFatal (self):
    """
    Enable this option if you want to return an error to the user for
    incorrect parameter values, even if they can be autocorrected.  This can
    be useful to show the user that 
    """
    self._parameterWarningsAreFatal = True
    pass

  def reportError (self,parameterError,immediate=False):
    """
    Report a parameter error to the portal.  @parameterError is an
    exception object of type ParameterError.  If @immediate is True,
    your script will exit immediately at this point with a dump of the
    errors (and fatal warnings, if enabled via
    Context.makeParameterWarningsFatal) in JSON format.  If @immediate
    is False, the errors will accumulate until Context.verifyParameters
    is called (and the errors will then be printed).
    """
    self._parameterErrors.append(parameterError)
    if immediate:
      self.verifyParameters()
    pass
  
  def reportWarning (self,parameterError):
    """
    Record a parameter warning.  Warnings will be printed if there are
    other errors or if warnings have been set to be fatal, when
    Context.verifyParameters() is called, or when there is another
    subsequent immediate error.
    """
    self._parameterWarnings.append(parameterError)
    pass
  
  def verifyParameters (self):
    """
    If there have been calls to Context.parameterError, and/or to
    Context.parameterWarning (and Context.makeParameterWarningsFatal has
    been called, making warnings fatal), this function will spit out some
    nice JSON-formatted exception info on stderr
    """
    if len(self._parameterErrors) == 0 \
         and (len(self._parameterWarnings) == 0 \
              or not self._parameterWarningsAreFatal):
      return 0

    #
    # Dump a JSON list of typed errors.
    #
    ea = []
    ea.extend(self._parameterErrors)
    ea.extend(self._parameterWarnings)
    json.dump(ea,sys.stderr,cls=PortalJSONEncoder)

    #
    # Exit with a count of errors and (fatal) warnings, multiplied by -100 ...
    # try to distinguish ourselves meaningfully!
    #
    retcode = len(self._parameterErrors)
    if self._parameterWarningsAreFatal:
      retcode += len(self._parameterWarnings)
    sys.exit(-100*retcode)
    pass
  
  @staticmethod
  def _legalList(l):
    return map(lambda x: x if not isinstance(x,tuple) else x[0], l)

  def _bindParametersCmdline (self):
    parser = argparse.ArgumentParser()
    for name in self._parameterOrder:
      opts = self._parameters[name]
      if opts['legalValues']:
        legal = Context._legalList(opts['legalValues'])
      else:
        legal = None
      parser.add_argument("--" + name,
                          type    = ParameterType.argparsemap[opts['type']],
                          default = opts['defaultValue'],
                          choices = legal,
                          help    = opts['description'])
    return parser.parse_args()

  def _bindParametersEnv (self):
    namespace = Namespace()
    paramValues= {}
    if self._readParamsPath:
        f = open(self._readParamsPath, "r")
        paramValues = json.load(f)
        f.close()
    for name in self._parameterOrder:
      opts = self._parameters[name]
      val = paramValues.get(name, opts['defaultValue'])
      if opts['legalValues'] and val not in Context._legalList(opts['legalValues']):
        # TODO: Not 100% sure what the right thing is to do here, need to get 
        # the error back in a nice machine-parsable form
        sys.exit("ERROR: Illegal value '%s' for option '%s'" % (val, name))
      setattr(namespace, name, ParameterType.argparsemap[opts['type']](val))
    return namespace

  def _dumpParamsJSON (self):
    #
    # Output the parameter dict in sorted order (sorted in terms of parameter
    # definition order).  This is correct, identical to json.dump (other than
    # key order), and much easier than subclassing json.JSONEncoder :).
    #
    didFirst = False
    f = open(self._dumpParamsPath, "w+")
    f.write('{')
    for name in self._parameterOrder:
      if didFirst:
        f.write(', ')
      else:
        didFirst = True
      opts = self._parameters[name]
      if opts.has_key('groupId') \
        and self._parameterGroups.has_key(opts['groupId']):
        opts['groupName'] = self._parameterGroups[opts['groupId']]
      json.dump(name,f)
      f.write(': ')
      json.dump(opts,f)
      pass
    f.write('}')
    f.close()
    return

  def _checkBind (self):
    if len(self._parameters) > 0 and not self._bindingDone:
      warnings.warn("Parameters were defined, but never bound with " +
          " bindParameters()", RuntimeWarning)

class PortalJSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o,PortalError):
      return o.__objdict__()
    else:
      # First try the default encoder:
      try:
        return json.JSONEncoder.default(self, o)
      except:
        try:
          # Then try to return a string, at least
          return str(o)
        except:
          # Let the base class default method raise the TypeError
          return json.JSONEncoder.default(self, o)
        pass
      pass
    pass
  pass

#
# Define some exceptions.  Everybody should subclass PortalError.
#
class PortalError (Exception):
  def __init__(self,message):
    self.message = message
    pass
  
  def __str__(self):
    return self.__class__.__name__ + ": " + self.message
    
  def __objdict__(self):
    retval = dict({ 'errorType': self.__class__.__name__, })
    for (k,v) in self.__dict__.iteritems():
      if k == 'errorType':
        continue
      if k.startswith('_'):
        continue
      retval[k] = v
    return retval

  pass

class ParameterError (PortalError):
  """
  A simple class to describe a parameter error.  If you need to report
  an error with a user-specified parameter value to the Portal UI,
  please create (don't throw) one of these error objects, and tell the
  Portal about it by calling Context.reportError.
  """
  def __init__(self,message,paramList):
    """
    Create a ParameterError.  @message is the overall error message;
    in the Portal Web UI, it will be displayed near each involved
    parameter for maximal impact.  @paramList is a list of the
    parameters that are involved in the error (often it is the
    combination of parameters that creates the error condition).
    The Portal UI will show this error message near *each* involved
    parameter to increase user understanding of the error.
    """
    self.message = message
    self.params = paramList
    
  pass

class ParameterWarning (PortalError):
  """
  A simple class to describe a parameter warning.  If you need to
  report an warning with a user-specified parameter value to the
  Portal UI, please create (don't throw) one of these error objects,
  and tell the Portal about it by calling Context.reportWarning .  The
  first time the Portal UI runs your geni-lib script with a user's
  parameter values, it turns on the "warnings are fatal" mode (and
  then warnings are reported as errors).  This gives you a chance to
  warn the user that they might be about to do something stupid,
  and/or suggest a set of modified values that will improve the
  situation.  .
  """
  def __init__(self,message,paramList,fixedValues={}):
    """
    Create a ParameterWarning.  @message is the overall error
    message; in the Portal Web UI, it will be displayed near each
    involved parameter for maximal impact.  @paramList is a list of
    the parameters that are involved in the warning (often it is the
    combination of parameters that creates the error condition).
    The Portal UI will show this warning message near *each*
    involved parameter to increase user understanding of the error.
    If you supply the @fixedValue dict, the Portal UI will change
    the values the user submitted to those you suggest (and it will
    tell them it did so).  You might want to supply @fixedValues for
    a proper warning, because if something is only a warning, that
    implies your script can and will proceed in the absence of
    further user input.  But sometimes we want to let the user know
    that a parameter change will occur, so we warn them and
    autocorrect!
    """
    self.message = message
    self.params = paramList
    self.fixedValues = fixedValues
    
  pass

class IllegalParameterDefaultError (PortalError):
  def __init__ (self,val):
    self._val = val 

  def __str__ (self):
    return "% given as a default value, but is not listed as a legal value" % self._val
