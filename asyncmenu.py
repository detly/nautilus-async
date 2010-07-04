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

class FakeMenuItem(nautilus.MenuItem):
    
    def __init__(self, label, sensitive=True):
        super(FakeMenuItem, self).__init__(
                                        "Fake::Fake",
                                        "%s" % label,
                                        "%s" % label,
                                        None)
        self.set_property('sensitive', sensitive)

class ItemResult(object):
    """
    Associates a nautilus.FileInfo object with an eventual result. The result
    of the asynchronous activity is stored in the "result" member.
    """
    
    def __init__(self, nautilus_file_info):
        self.item = nautilus_file_info
        self.result = None    

class AsyncBackgroundMenuProvider(nautilus.MenuProvider):
    """
    WARNING: I have not fully tested the "in_update_signal" mechanism.
    """
    def __init__(self):
        self.provider = None
        self.items = {}
        self.in_update_signal = False
        self.uris_requested_for_update = set()

    def schedule_menu_work(self, uri):
        # Let's just make something up to demonstrate
        sys.stderr.write("Scheduling: %s\n" % uri)
        glib.timeout_add_seconds(
                        TIMEOUT,
                        self.menu_work_complete,
                        uri,
                        42)

    def get_background_items_initial(self, folder):
        return [FakeMenuItem("Please wait...", False)]
        
    def get_background_items_final(self, folder, result):
        return [FakeMenuItem("Menu item for: %s" % result)]
    
    def get_background_items_full(self, provider, window, folder):
                
        if self.provider is None:
            self.provider = provider
        
        uri = folder.get_uri()
        
        sys.stderr.write("Requesting: %s\n" % uri) 
        sys.stderr.write("In update signal: %s\n" % self.in_update_signal)
                
        if self.in_update_signal:
            result = self.items[uri].result
            items = self.get_background_items_final(folder, result)
            self.uris_requested_for_update.add(uri)
        else:
            self.items[uri] = ItemResult(folder)
            items = self.get_background_items_initial(folder)
            self.schedule_menu_work(uri)
        
        return items

    def menu_work_complete(self, uri, result):
        
        # IMPORTANT: long delays in this function will make Nautilus, and
        # possibly the whole GNOME session, lock up.
        
        sys.stderr.write("Completed work for %s\n" % uri)
        
        self.items[uri].result = result
                
        self.in_update_signal = True
        self.emit_items_updated_signal(self.provider)
        self.in_update_signal = False

        for uri_key in self.items.keys():
            # We can check what items were requested inside the
            # "get_background_items_full" call INSIDE the update signal.
            # Whatever is not in that list, we can discard.
            if uri_key not in self.uris_requested_for_update:
                sys.stderr.write("Deleting URI from dict: %s\n" % uri)
                del self.items[uri_key]
        
        self.uris_requested_for_update.clear()
        
        sys.stderr.write("Items remaining:\n\t")
        sys.stderr.write("\n\t".join(self.items.keys()) + "\n")
        
