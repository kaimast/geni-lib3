Importing a Context from the GENI Portal
========================================

In order to communicate with any federation resource using ``geni-lib`` you need to construct
a ``Context`` object that contains information about the framework you are using (for example
ProtoGENI, Emulab, GENI Clearinghouse, etc.), as well as your user information (SSH keys,
login username, federation urn, etc.).  This simple tutorial will walk you through the easiest
way to create a ``Context`` if you have an account at the `GENI Portal <http://portal.geni.net>`_.

========================
Download The omni.bundle
========================

First we need a file called ``omni.bundle`` which is available from the GENI Portal web
interface.  Once you log into the GENI Portal you can use the following steps to locate your
``omni.bundle`` download:

* At the top of the Portal home page click on the tab labeled **Profile**
* In the tabs on the Profile page click on the one labeled **Configure omni**
* Embedded in the text under the **Option 1: Automatic omni configuration** header, there
  is a button labeled **Download your omni data**.  Click this button.

.. note::
  If you see a warning that no SSH keys have been uploaded you can still use the bundle, but
  you will need to specify an SSH public key path in a later step.

* Click the **Download your omni data** button at the bottom of the next page and it should
  start downloading immediately in your browser.

=======================
Run Context Import Tool
=======================

A script called ``context-from-bundle`` was installed as part of your ``geni-lib``
installation, which can convert your ``omni.bundle`` into the data necessary for ``geni-lib``
to create a ``Context`` object for you.  The instructions for using this tool are below -
choose the section appropriate for your OS.

---------------
MacOS X / Linux
---------------

In most installations your path should already include the import tool and it should run
cleanly without any additional configuration::

  $ context-from-bundle --bundle /path/to/omni.bundle

If no arguments are supplied the bundle is assumed to be in the current directory.  If your
bundle does not contain an SSH public key you will be required to supply a path to one using
the ``--pubkey`` argument at the command line.

-------
Windows
-------

Unfortunately the default Python installation on Windows does not add the site Scripts
directory to your path, so you need to invoke it directly.  If you are using Python 2.8 you
will need to replace ``Python27`` with ``Python28`` below::

  C:\> python C:\Python27\Scripts\context-from-bundle --bundle path\to\omni.bundle

If no arguments are supplied the bundle is assumed to be in the current directory.  If your
bundle does not contain an SSH public key you will be required to supply a path to one using
the ``--pubkey`` argument at the command line.

============
Test It Out!
============

Now we can take your newly imported information, instantiate our context, and query an aggregate::

   $ python
   >>> import geni.util
   >>> context = geni.util.loadContext()
   >>> import geni.aggregate.instageni as IG
   >>> import pprint
   >>> pprint.pprint(IG.GPO.getversion(context))
   {'code': {'am_code': 0,
             'am_type': 'protogeni',
             'geni_code': 0,
             'protogeni_error_log': 'urn:publicid:IDN+instageni.gpolab.bbn.com+log+abedbcc20e6defe716eb83b8586c7e08',
             'protogeni_error_url': 'https://boss.instageni.gpolab.bbn.com/spewlogfile.php3?logfile=abedbcc20e6defe716eb83b8586c7e08'},
   ...snip...

You should get a large structure of formatted output telling you version and configuration
information about the GPO InstaGENI aggregate.  If you get any errors read them thorougly and
review what they may be telling you about any mistakes you may have made.  You can also ask your
instructor if at an in-person tutorial.

=========
Finished!
=========

Assuming you have experienced no errors, your ``geni-lib`` installation is now set up and
can communicate with all aggregates in the federation.  If you have any issues you can
send a message to the `geni-users <https://groups.google.com/forum/#!forum/geni-users>`_
google group for help.

