.. Copyright (c) 2015  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

VTS: Basic WAN Topology
=======================

This example walks through creating a two-site WAN topology with one forwarding
element at each site.  Like all VTS reservations that require compute resources,
the resources for each site will come from two different aggregate managers.
This example also employs further sequencing constraints in order to build the
WAN circuit.

In order to build a circuit between two sites, those sites need to share a
common **circuit plane**.  This is simply a named substrate that both sides have
a common attachment to.  In this tutorial we will use the ``geni-mesoscale``
circuit plane, which is currently available at all GENI VTS sites (but is
scheduled to be decommissioned by mid-2015 at the latest).  Future reservations
will still be able to make WAN circuits over GENI, but it will rely on getting
advertisements from VTS aggregates and finding the new shared **circuit plane**.
