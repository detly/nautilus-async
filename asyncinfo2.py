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
TIMEOUT = 3

def schedule_background_work(uri, callback):
    glib.timeout_add_seconds(TIMEOUT, callback, uri)

class ItemResult(object):
    
    def __init__(self, nautilus_file_info):
        self.item = nautilus_file_info
        self.result = None    

class AsyncInfoProvider2(nautilus.InfoProvider):

    # These methods are all called synchronously. We're fine.

    def __init__(self):
        self.nodes_awaiting_update = {}

    def update_info_initial(self, item):
        pass

    def update_info_final(self, item, result):
        if result:
            item.add_emblem("emblem-generic")

    def update_file_info(self, item):
                
        uri = item.get_uri()
        
        item_result = self.nodes_awaiting_update.get(uri) 
        
        if item_result is None:
            # If we don't have an nautilus.FileInfo item stored then this is the
            # first time we've been called (either at all, or since the last
            # callback caused the status to update). Store the item, so we can
            # get it back later, and use something serialisable to map to it.
            self.nodes_awaiting_update[uri] = ItemResult(item)
            schedule_background_work(uri, self.file_info_callback)
            self.update_info_initial(item)
        elif item_result.result is not None:
            # This means that we are being called from INSIDE
            # invalidate_extension_info - in other words, we're in the callback
            result = item_result.result
            del self.nodes_awaiting_update[uri]
            self.update_info_final(item, result)
        else:
            # This means that we've been called again while *waiting* for the
            # async activity to complete. In which case, update the item object
            # just in case it's changed, but don't do anything else.
            self.nodes_awaiting_update[uri] = ItemResult(item)
        
    def file_info_callback(self, uri):
        
        item_result = self.nodes_awaiting_update.get(uri)
        
        if item_result is not None:
            item_result.result = True
            item_status.item.invalidate_extension_info()
            # Edge case: item is deleted before this callback is called
        
        # else: something went wrong
            
        
