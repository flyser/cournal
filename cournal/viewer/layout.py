#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Fabian Henze
# 
# Cournal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cournal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cournal.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gdk

from . import PageWidget

class Layout(Gtk.Layout):
    def __init__(self, document, **args):
        Gtk.Layout.__init__(self, **args)
        self.doc = document
        self.children = []
        
        for page in self.doc.pages:
            self.children.append(PageWidget(page))
            self.put(self.children[-1], 0, 0)
     
    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)

        new_width = allocation.width
        new_height = allocation.width*self.doc.height/self.doc.width + 5*(len(self.doc.pages)-1)
        old_width, old_height = self.get_size()
        
        if old_width != new_width:
            #print("Ly: size_allocate")
            self.set_size(new_width, new_height)
            y_shift = 0
            for child in self.children:
                y_shift += self.allocate_child(child, 0, y_shift, new_width) + 5
        
        # Shamelessly copied from the GtkLayout source code:
        if self.get_realized():
            self.get_window().move_resize(allocation.x, allocation.y,
                                          allocation.width, allocation.height)
            self.get_bin_window().resize(max(allocation.width, new_width),
                                         max(allocation.height, new_height))
    
    def allocate_child(self, child, x, y, width):
        r = Gdk.Rectangle()
        r.x = x
        r.y = y
        r.width = width
        r.height = child.do_get_preferred_height_for_width(width)[0]
        child.size_allocate(r)
        return r.height
