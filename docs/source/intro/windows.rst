Windows 7 (32-bit)
==================

These instructions may work on later versions of Windows, and/or 64-bit versions, but they have not been tested.

=========================
Installation Dependencies
=========================

* Mercurial 3.1.2 (http://mercurial.selenic.com/wiki/Download)
* Python 2.7.8 (http://www.python.org)
* Omni 2.7 (http://trac.gpolab.bbn.com/gcf/wiki/Omni)

=====================
Install / Basic Setup
=====================

* Install the above dependencies in their default locations (particularly Python and Omni 2.7)

  If you change any of the install locations you may need to edit configuration files

* Open a command line (``cmd.exe``) and clone the geni-lib repository::

   C:\Development> hg clone http://bitbucket.org/barnstorm/geni-lib
   C:\Development> cd geni-lib

* Run the batch file in the support/ directory that sets up your environment::

   C:\Development> support/envsetup.bat

Congratulations, you are now ready to launch ``python`` and import geni lib modules!

You can also make a shortcut to ``cmd.exe`` and change the "target" property to
include the environment setup script::

  C:\Windows\System32\cmd.exe /k "C:\Development\geni-lib\support/envsetup.bat"

(The location of ``geni-lib`` can be changed, just alter these paths accordingly)
