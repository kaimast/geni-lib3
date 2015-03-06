.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

Basic Single-Site VTS Topology
==============================

This example walks through creating a simple VTS topology with one Open vSwitch
datapath connected to two virtual machines provided by the site compute
aggregate. Resources for this request will come from two different aggregate
managers at the same site, using information returned from one aggregate to
structure the 2nd request.

The resultant topology will be as in the diagram below.  The resources are
color-coded to indicate which aggregate will provision them:

.. image:: images/vts-simple.*

This obviously has no advantage over having the local site compute aggregate
connect the VMs directly, but it serves as the simplest example of how to
stage the provisioning of VTS resources and forms the basis for more advanced
use cases.


