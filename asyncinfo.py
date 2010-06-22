"""
Copyright (C) 2010 by Jason Heeris <jason.heeris@gmail.com>

nautilus-async is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

nautilus-async is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
nautilus-async;  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import sys

import nautilus

import glib

# Period in seconds for really long function
TIMEOUT = 3
        
def make_fake_menu_item(num):
        return nautilus.MenuItem(
                        "Fake: %s %i" % num,
                        "Fake: %s #%i" % num,
                        "Fake: %s #%i" % num,
                        None)

def schedule_background_work(uri, callback):
    glib.timeout_add_seconds(TIMEOUT, callback, uri)

class ItemStatus(object):
    
    def __init__(self, nautilus_file_info):
        self.item = nautilus_file_info
        self.status = None
        
class AsyncInfoProvider(nautilus.InfoProvider):

    # These methods are all called synchronously. We're fine.

    def __init__(self):
        self.nodes_awaiting_update = {}

    def update_file_info(self, item):
        
        uri = item.get_uri()
        
        sys.stderr.write("** Info request for: %s\n" % uri)
        
        if uri not in self.nodes_awaiting_update:
            sys.stderr.write("** Requesting check for: %s\n" % uri)
            self.nodes_awaiting_update[uri] = item
            schedule_background_work(uri, self.update_file_info_callback)
            status = False

    def update_file_info_callback(self, uri):
        
        item = self.nodes_awaiting_update.get(uri)
        
        if item is not None:
            sys.stderr.write("Updating: %s\n" % uri)
            item.add_emblem("emblem-generic")
            del self.nodes_awaiting_update[uri]

        # else: something went wrong
            
        
