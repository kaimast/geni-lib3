.. Copyright (c) 2016  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Creating and Managing Projects
==============================

This example will walk you through creating a project at the NSF GENI Clearinghouse
and managing membership.

.. note::
  You will need to have sufficient privileges in order to perform these operations.  If you
  are a project admin but cannot create projects (or already have one you want to use), you
  can still use the examples below to manage project membership.

Create Project
--------------

In order to create a project, you need three pieces of information to give to the Clearinghouse:

* Project Name

  .. note::
    Names must be unique for all projects at a given Clearinghouse and you will get an error
    if you happen to choose a name which has already been used.  If you are likely to create
    multiple projects for similar purposes (different sections of the same class, etc.), you
    may want to include date and organization information in your name (e.g. spr17-UH-cs410),
    in order to use consistent names which are still unique.

* Expiration Date
* Project Description

.. warning::
  Projects can not be manually deleted from most Clearinghouses, so if you are just testing out this
  functionality please set a short expiration date so that it will expire out of the system.


Using your existing ``context`` that is set up for the Clearinghouse where you want to create a
project, you can set up your values and make a single call to create your project::

  >>> import datetime

  >>> name = "prj-test-1"
  >>> desc = "My test project"
  >>> exp = datetime.datetime.now() + datetime.timedelta(hours=12)

  >>> prjinfo = context.cf.createProject(context, name, exp, desc)

An exception will be raised if this action fails, otherwise ``prjinfo`` will contain information
about our new project returned from the Clearinghouse::

  >>> from pprint import pprint as PP
  >>> PP(prjinfo)
  {'PROJECT_CREATION': '2017-01-11T02:24:29Z',
   'PROJECT_DESCRIPTION': 'My test project',
   'PROJECT_EXPIRATION': '2017-01-11T03:23:49Z',
   'PROJECT_EXPIRED': False,
   'PROJECT_NAME': 'prj-test-1',
   'PROJECT_UID': '8bbfa399-efcd-4a1d-bb74-932213d8491f',
   'PROJECT_URN': 'urn:publicid:IDN+ch.geni.net+project+prj-test-1',
   '_GENI_PROJECT_EMAIL': None,
   '_GENI_PROJECT_OWNER': '8a447f06-8bd5-4f32-8fd6-1a3528e7fa37'}

For the most part this information is not important - just remember the name you gave your
project so that you can add members and make slices.  Your ``geni-lib`` context has an
attribute for the "current" project, which you should set whenever you are working with this
project::

  >>> context.project = "prj-test-1"

Of course if you have multiple projects, you'll need to change the value of ``context.project``
as you change which project you are working with.
    
Listing Your Projects
---------------------

Add Members to Project
----------------------

Remove Members from Project
---------------------------
