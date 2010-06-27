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

class AsyncInfoProvider(nautilus.InfoProvider):
    """
    This is currently more of a template than a base class, but it is designed
    so that the following methods can be overridden to do something useful:
    
    schedule_background_work() - does the asynchronous work 
    update_info_final() - eventual response to callback result
    
    Do NOT just try to inherit from it by defining a new class IN THE SAME FILE
    and putting it where Nautilus will find it - Nautilus will see both the
    super- and subclass as extensions and attempt to use them both.
    """
    
    # These methods are all called synchronously. We're fine.

    def __init__(self):
        # Do not attempt to initialise super classes.
        self.nodes_awaiting_update = {}


    def schedule_background_work(self, uri):
        """
        This gets called to do the asynchronous work. It should return as soon
        as possible, delegating all work to another process. When it is done, it
        should call "background_work_complete" with the URI that was given here
        and the result from the background task.
        
        Do not use threads, they will not work under Nautilus.
        
        If scheduling the background work *still* has too much latency, I
        recommend using glib's "idle_add" method.        
        
        @param uri the URI of the item for which the information was requested
                   (this is a URL-encoded string)
        """
        # Let's just make something up to demonstrate
        glib.timeout_add_seconds(
                        TIMEOUT,
                        self.background_work_complete,
                        uri,
                        42)

    def update_info_final(self, item, result):
        """
        Called when the asynchronous work is compeleted and triggeres the
        callback. The result of the asynchronous work is passed in.
        
        @param item a nautilus.FileInfo object
        @param result the result of the asynchronous work
        """
        if result:
            item.add_emblem("emblem-generic")


    def update_file_info(self, item):
        """ This is the hook for the nautilus extension API. """
        uri = item.get_uri()
        
        if uri not in self.nodes_awaiting_update:
            self.nodes_awaiting_update[uri] = item
            self.schedule_background_work(uri)

    def background_work_complete(self, uri, result):
        """
        This handles the result of the asynchronous activity, which ends up
        getting passed to "update_info_final()". It takes the URI that was given
        "schedule_background_work" and a single result (that may change to a
        more flexible user data system).
        
        This method is not meant to be overridden.
        
        @param uri the URI that was given to the scheduling method IN EXACTLY
                   THE SAME FORM
        @param result the result of the callback
        """
        
        item = self.nodes_awaiting_update.pop(uri, None)
        
        if item is not None:
            self.update_info_final(item, result)
            # Edge case: item is deleted before this callback is called
        
        
