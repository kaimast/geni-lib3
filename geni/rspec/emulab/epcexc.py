from __future__ import absolute_import

#
# Common EPC exception classes
#

class InvalidRole(Exception):
    def __init__(self, role):
        self.role = role
    def __str__(self):
        return "Warning: Invalid EPC role: %s" % role

class InvalidRequestRSpec(Exception):
    def __str__(self):
        return "Error: Not a valid Request RSpec!"

class UnboundRSpec(Exception):
    def __str__(self):
        return "Error: RSpec must be bound before instantiation!"
