.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

Basic Single-Site VTS Topology
==============================

This example walks through creating a simple VTS topology with one forwarding
element (an Open vSwitch instance) connected to two virtual machines provided
by the site compute aggregate. Resources for this request will come from two
different aggregate managers at the same site, using information returned from
the VTS aggregate to structure the second request to the compute aggregate.

The resultant topology will be as in the diagram below.  The resources are
color-coded to indicate which aggregate will provision them:

.. image:: images/vts-simple.*

This obviously has no advantage over having the local site compute aggregate
connect the VMs directly, but it serves as the simplest example of how to
stage the provisioning of VTS resources and forms the basis for more advanced
use cases.

.. note::
  This example requires that you have set up a valid context object with GENI
  credentials.

Walk-through
------------

For this example we'll use InstaGENI compute resources, but this would work
for ExoGENI sites that have VTS support as well if you change the InstaGENI
imports to the relevant ones for ExoGENI.

* We need to set up basic imports to create requests and send them to the
aggregate::

  import geni.rspec.pg as PG
  import geni.rspec.igext as IGX
  import geni.rspec.vts as VTS

  import geni.aggregate.instageni as IGAM
  import geni.aggregate.vts as VTSAM

* VTS reservations are a two-stage process, where the VTS resources must be
reserved first and the results used to create the proper compute request::

  vtsr = VTS.Request()

* First we select the image we want to use for our VTS forwarding elements::

  image = VTS.OVSL2Image()

.. note::
  Images support varying functionality that can be configured here, such as
  sflow and netflow collectors, openflow controllers, etc.

* We then instantiate a single forwarding element with this image, and request
two local circuits to connect to our VMs::

  felement = VTS.Datapath(image, "fe0")
  felement.attachPort(VTS.LocalCircuit())
  felement.attachPort(VTS.LocalCircuit())
