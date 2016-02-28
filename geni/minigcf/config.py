# Copyright (c) 2015-2016  Barnstormer Softworks, Ltd.

#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

class HTTP(object):
  """Global configuration options for MiniGCF HTTP(S) calls."""

  TIMEOUT = 30
  """Initial response timeout.  Note that this is not the time limit on the entire
  download, just the initial server response."""

  ALLOW_REDIRECTS = False
  """Allow MiniGCF to follow HTTP redirects (301)."""

  LOG_RAW_RESPONSES = False
  """If set to a valid `(log_handle, log_level)` tuple, will write all raw responses
  (before any parsing) from AM API and CH API calls to that log at the given level."""

