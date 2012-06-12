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

PAGE_SEPARATOR = 10 # px

class Layout(Gtk.Layout):
    def __init__(self, document, **args):
        Gtk.Layout.__init__(self, **args)
        self.document = document
        self.children = []
        self.zoomlevel = 1
        
        #color =
        #print(color)
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(79/255,78/255,77/255,1))
        for page in self.document.pages:
            self.children.append(PageWidget(page))
            self.put(self.children[-1], 0, 0)
    
    def get_height_for_width(self, width):
        return width * self.document.height / self.document.width
    
    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)

        new_width = allocation.width*self.zoomlevel
        old_width, old_height = self.get_size()
        adjustment = self.get_vadjustment()
        
        if old_width != new_width:
            #print("Ly: size_allocate")
            new_height = 0
            for child in self.children:
                new_height += self.allocate_child(child, 0, new_height, new_width)
                new_height += PAGE_SEPARATOR
            new_height -= PAGE_SEPARATOR
            # Preserve position when the window is resized.
            adjustment.set_value(adjustment.get_value() * new_height / old_height)
        else:
            new_height = old_height
        self.set_size(new_width, new_height)
        # Shamelessly copied from the GtkLayout source code:
        if self.get_realized():
            self.get_window().move_resize(allocation.x, allocation.y,
                                          allocation.width, allocation.height)
            self.get_bin_window().resize(new_width, max(allocation.height, new_height))
    
    def allocate_child(self, child, x, y, width):
        r = Gdk.Rectangle()
        r.x = x
        r.y = y
        r.width = width
        r.height = child.do_get_preferred_height_for_width(width)[0]
        child.size_allocate(r)
        return r.height
    
    def set_zoomlevel(self, absolute=None, change=None):
        if absolute:
            self.zoomlevel = absolute
        elif change:
            self.zoomlevel += change
        self.zoomlevel = min(max(self.zoomlevel, 0.2),3)
        self.do_size_allocate(self.get_allocation())
