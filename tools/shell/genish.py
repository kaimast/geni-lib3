# Copyright (c) 2015  Barnstormer Softworks, Ltd.

import os
import os.path
import code

#import geni._coreutil as GCU

class Shell(object):
  def run (self, options):
    imports = {}

    try:
      import readline
    except ImportError:
      pass
    else:
      import rlcompleter
      readline.set_completer(rlcompleter.Completer(imports).complete)
      readline.parse_and_bind("tab:complete")

    # We want to honor both $PYTHONSTARTUP and .pythonrc.py, so follow system
    # conventions and get $PYTHONSTARTUP first then .pythonrc.py.
    for pythonrc in (os.environ.get("PYTHONSTARTUP"), '~/.pythonrc.py'):
      if not pythonrc:
        continue
      pythonrc = os.path.expanduser(pythonrc)
      if not os.path.isfile(pythonrc):
        continue
      try:
        with open(pythonrc) as handle:
          exec(compile(handle.read(), pythonrc, 'exec'), imports)
      except NameError:
        pass

    import geni.util
    import geni.rspec.pg
    import geni.rspec.vts
    import geni.aggregate.instageni
    import geni.aggregate.vts
    import geni.aggregate.exogeni

    imports["util"] = geni.util
    imports["PG"] = geni.rspec.pg
    imports["VTS"] = geni.rspec.vts
    imports["IGAM"] = geni.aggregate.instageni
    imports["VTSAM"] = geni.aggregate.vts
    imports["EGAM"] = geni.aggregate.exogeni

    code.interact(local=imports)

if __name__ == '__main__':
  s = Shell()
  s.run(None)
