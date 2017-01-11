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
    Names must be unique for all projects at a given Clearinghouse. You will get an error
    if you happen to choose the name of an existing project.

* Expiration Date
* Project Description

.. warning::
  Projects can not be manually deleted from most Clearinghouses, so if you are just testing out this
  functionality please set a short expiration date so that it will expire out of the system.


Using your existing ``context`` that is set up for the Clearinghouse where you want to create a
project, you can set up your values and make a single call to create your project::

  import datetime

  name = "prj-test-1"
  desc = "My test project"
  exp = datetime.datetime.now() + datetime.timedelta(hours=6)

  context.cf.createProject(context, name, exp, desc)


    
Add Members to Project
----------------------

Remove Members from Project
---------------------------
