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

   C:\> mkdir C:\Development
   C:\> cd C:\Development
   C:\Development> hg clone http://bitbucket.org/barnstorm/geni-lib
   C:\Development> cd geni-lib

.. note::
  (The location of ``geni-lib`` can be changed, just alter these paths accordingly)

* Run the batch file in the support/ directory that sets up your environment::

   C:\Development\geni-lib> support\envsetup.bat

Congratulations, you are now ready to launch ``python`` and import geni lib modules!

You can also make a shortcut to ``cmd.exe`` and change the "target" property to
include the environment setup script::

  C:\Windows\System32\cmd.exe /k "C:\Development\geni-lib\support\envsetup.bat"


=====================
Extended Dependencies
=====================

Some of the applications in the ``tools/`` directory require additional dependencies.  For the most part
these dependencies can be installed using ``pip``, but ``pip`` is not included in the Python 2.7
distribution by default on windows.

You can install ``pip`` on Windows 7 and later by launching ``Powershell`` (not ``cmd.exe``) and doing::

  PS C:\> $client = new-object System.Net.WebClient
  PS C:\> $client.DownloadFile("http://bootstrap.pypa.io/get-pip.py", "C:/Development/get-pip.py")

Note that the second argument must be a valid full path.  Remember where you placed this file.

Now, open ``cmd.exe`` and run the batch file that sets up the geni-lib environment (or use your previously
created shortcut), and do the following::

  C:\> cd C:\Development
  C:\Development> python get-pip.py

Now you can use ``pip`` to install new dependencies that the additional tools may require.
