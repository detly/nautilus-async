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

class AsyncBackgroundMenuProvider(nautilus.MenuProvider):
    
    def __init__(self):
        self.provider = None
        self.items = {}

    def get_items_initial(self, uri):
        return [FakeMenuItem("Please wait...", False)]
    
    def calculate_items_for_result(self, uri, result):
        return [FakeMenuItem("Menu item for: %s" % result)]
        
    def get_background_items_full(self, provider, window, folder):
        if self.provider is None:
            self.provider = provider
        
        return self.calculate_items_for_result(folder.get_uri(), "Blah")
        
