.. Copyright (c) 2016  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Vagrant
=======

geni-lib can be installed on any platform that supports Vagrant using the instructions
below.

The Vagrant VM created by this process automatically sets up your geni-lib context and
provides a web interface for creating `Jupyter <http://jupyter.org>`_ notebooks using GENI resources.

=========================
Installation Dependencies
=========================

Install these dependencies before creating the Vagrant VM.

* VirtualBox (https://www.virtualbox.org/wiki/Downloads)
* Vagrant (https://www.vagrantup.com/downloads.html)

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
  you will need to provide an SSH public key path in a later step.

* Click the **Download your omni data** button at the bottom of the next page and it should
  start downloading immediately in your browser.

==============================
Set up your geni-lib directory
==============================

* Create a directory on your system named ``genivm`` to hold your GENI environment
* Copy your ``omni.bundle`` to this directory
* Download the ``geni-lib`` Vagrant setup file to this directory
 * On systems with ``curl`` (MacOS X, Linux) you can use the following command::

    curl -O https://bitbucket.org/barnstorm/geni-lib/raw/tip/support/Vagrantfile
  
 * On Windows systems with Powershell you can use the following::

    PS C:\genivm> $client = new-object System.Net.WebClient
    PS C:\genivm> $client.DownloadFile("https://bitbucket.org/barnstorm/geni-lib/raw/tip/support/Vagrantfile", "C:/genivm/Vagrantfile")

 * You can also download the above URL with a web browser and save it in your ``genivm`` directory

* Create your vagrant vm using ``vagrant up`` in this directory

.. note::
  This may take a long time (20+ minutes) depending on the speed of your internet connection

==============================
Load the Jupyter web interface
==============================

* Open any web browser and load ``http://localhost:8888``
* In the upper right-hand corner of the UI, choose ``New->(Notebooks) Python 2`` from the dropdown menu
* In the new notebook enter ``%load_ext genish`` in the first cell and enter your key passphrase if necessary
  (otherwise just hit enter to skip the passphrase entry)

Congratulations, ``geni-lib`` is now loaded and ready for use in your web browser!
