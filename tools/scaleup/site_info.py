#--------------------------------------------------------------------
# Copyright (c) 2014 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
# ----------------------------------------------------------------------

"""
List stitching InstaGENI site, and total list of InstaGENI site. 

Both stitch_site and ig_site dicts should be updated if a new stitching site is added.

@author: xliu
"""

import geni.aggregate.instageni as ig
#import geni.aggregate.exogeni as eg

stitch_site = {0: ig.GPO,
               1: ig.NYSERNet,
               2: ig.Illinois,
               3: ig.MAX,
               4: ig.Missouri,
               5: ig.Utah,
               6: ig.Wisconsin,
               7: ig.Stanford,
               8: ig.UtahDDC,}
               
               
ig_site = {0: ig.GPO,
           1: ig.NYSERNet,
           2: ig.Illinois,
           3: ig.MAX,
           4: ig.Missouri,
           5: ig.Utah,
           6: ig.Wisconsin,
           7: ig.Stanford,
           8: ig.UtahDDC,
           9: ig.Kentucky,
           10: ig.Clemson,
           11: ig.Cornell,
           12: ig.GATech,
           13: ig.Kansas,
           14: ig.Northwestern,
           15: ig.NYU,
           16: ig.Rutgers,
           17: ig.Princeton,
           18: ig.Dublin,
           19: ig.CaseWestern,
           20: ig.MOXI,
           21: ig.SOX,
           22: ig.NPS,
           23: ig.Kettering,
           24: ig.LSU,
           25: ig.CENIC,}




