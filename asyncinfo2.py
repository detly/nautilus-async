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

# Period in seconds for our pretend really-long-function
TIMEOUT = 3

class ItemResult(object):
    """
    Associates a nautilus.FileInfo object with an eventual result. The result
    of the asynchronous activity is stored in the "result" member.
    """
    
    def __init__(self, nautilus_file_info):
        self.item = nautilus_file_info
        self.result = None    

class AsyncInfoProvider2(nautilus.InfoProvider):
    """
    This is currently more of a template than a base class, but it is designed
    so that the following methods can be overridden to do something useful:
    
    schedule_background_work() - does the asynchronous work 
    update_info_initial() - initial response to info request
    update_info_final() - eventual response to callback result
    
    Do NOT just try to inherit from it by defining a new class IN THE SAME FILE
    and putting it where Nautilus will find it - Nautilus will see both the
    super- and subclass as extensions and attempt to use them both.
    """
    
    # Note that Nautilus calls all methods asynchronously.

    def __init__(self):
        # Do not attempt to initialise super classes.
        self.nodes_awaiting_update = {}


    def schedule_info_work(self, uri):
        """
        This gets called to do the asynchronous work. It should return as soon
        as possible, delegating all work to another process. When it is done, it
        should call "info_work_complete" with the URI that was given here and
        the result from the background task.
        
        Do not use threads, they will not work under Nautilus.
        
        If scheduling the background work *still* has too much latency, I
        recommend using glib's "idle_add" method.
        
        @param uri the URI of the item for which the information was requested
                   (this is a URL-encoded string)
        """
        # Let's just make something up to demonstrate
        glib.timeout_add_seconds(
                        TIMEOUT,
                        self.info_work_complete,
                        uri,
                        42)

    def update_info_initial(self, item):
        """
        Called when the update_file_info method is called and we haven't
        yet invoked our asynchronous activity.
        
        @param item a nautilus.FileInfo object
        """
        pass

    def update_info_final(self, item, result):
        """
        Called when the update_file_info is called as a result of invalidating
        the extension info for the given item. This means that the callback has
        completed, the result of which is passed in.
        
        @param item a nautilus.FileInfo object
        @param result the result of the asynchronous work
        """
        if result:
            item.add_emblem("emblem-generic")

    def update_file_info(self, item):
        """ This is the hook for the nautilus extension API. """                
        uri = item.get_uri()
        
        item_result = self.nodes_awaiting_update.get(uri) 
        
        if item_result is None:
            # If we don't have an nautilus.FileInfo item stored then this is the
            # first time we've been called (either at all, or since the last
            # callback caused the status to update). Store the item, so we can
            # get it back later, and use something serialisable to map to it.
            self.nodes_awaiting_update[uri] = ItemResult(item)
            self.update_info_initial(item)
            self.schedule_info_work(uri)
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
        
    def info_work_complete(self, uri, result):
        """
        This handles the result of the asynchronous activity, which ends up
        getting passed to "update_info_final()". It takes the URI that was given
        "schedule_info_work" and a single result (that may change to a more
        flexible user data system).
        
        This method is not meant to be overridden.
        
        @param uri the URI that was given to the scheduling method IN EXACTLY
                   THE SAME FORM
        @param result the result of the callback
        """
        
        item_result = self.nodes_awaiting_update.get(uri)
        
        if item_result is not None:
            item_result.result = result
            item_result.item.invalidate_extension_info()
            # Edge case: item is deleted before this callback is called
        
        # else: something went wrong
            
        
    
