"""
Copyright (C) 2010 by Jason Heeris <jason.heeris@gmail.com>

nautilus-async is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

nautilus-async is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with nautilus-async;  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import sys

import nautilus
import glib

# Period in seconds for really long function
TIMEOUT = 6

def schedule_background_work(uri, callback):
    gobject.idle_add(TIMEOUT, callback, uri)

class ItemStatus(object):
    
    def __init__(nautilus_file_info):
        self.item = nautilus_file_info
        self.status = None    

class AsyncInfoProvider2(nautilus.InfoProvider):

    # These methods are all called synchronously. We're fine.

    def __init__(self):
        self.nodes_awaiting_update = {}

    def update_status(self, item, status):
        if status:
            item.add_emblem("emblem-generic")

    def update_file_info(self, item):
                
        uri = item.get_uri()
        
        item_status = self.nodes_awaiting_update.get(uri) 
        
        if item_status is None:
            self.nodes_awaiting_update[uri] = ItemStatus(item)
            schedule_background_work(uri, self.update_file_info_callback)
            status = False
        elif item_status.status is not None:
            status = item_status.status
            del self.nodes_awaiting_update[uri]
        
        
    def update_file_info_callback(self, uri):
        
        item_status = self.nodes_awaiting_update.get(uri)
        
        if item_status is not None:
            item_status.status = True
            item_status.item.invalidate_extension_info()
            # Edge case: item is deleted before this callback is called
        
        # else: something went wrong
            
        
