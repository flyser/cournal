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

from cournal.viewer.pagewidget import PageWidget

PAGE_SEPARATOR = 10 # px

class Layout(Gtk.Layout):
    """
    The main pdf viewer/annotation widget containing one or more PageWidgets.
    """
    
    def __init__(self, document, **args):
        """
        Constructor
        
        Positional arguments:
        document -- A Document object, containing the pages we want to render.
        
        Keyword arguments:
        **args -- Arguments passed to the Gtk.Layout constructor
        """
        Gtk.Layout.__init__(self, **args)
        self.document = document
        self.children = []
        self.zoomlevel = 1
        
        # The background color is visible between the PageWidgets
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(79/255, 78/255, 77/255, 1))
        
        for page in self.document.pages:
            self.children.append(PageWidget(page, self))
            self.put(self.children[-1], 0, 0)
    
    def do_size_allocate(self, allocation):
        """
        Called, when the Layout is about to be resized. Resizes all children.
        
        Positional arguments:
        allocation -- Gtk.Allocation object (containing the new height and width)
        """
        self.set_allocation(allocation)

        new_width = allocation.width*self.zoomlevel
        old_width, old_height = self.get_size()
        adjustment = self.get_vadjustment()
        
        if old_width != new_width:
            new_height = 0
            for child in self.children:
                new_height += self.allocate_child(child, 0, new_height, new_width)
                new_height += PAGE_SEPARATOR
            new_height -= PAGE_SEPARATOR
            # Preserve position when the window is resized.
            adjustment.set_upper(adjustment.get_upper() * new_height / old_height)
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
        """
        Allocate space for a child widget
        
        Positional arguments:
        child -- The child widget (likely a PageWidget)
        x -- The x coordinate of the child
        y -- The y coordinate of the child
        width -- The width of the child
        
        Return value: height of the child widget
        """
        r = Gdk.Rectangle()
        r.x = x
        r.y = y
        r.width = width
        r.height = child.get_preferred_height_for_width(width)[0]
        child.size_allocate(r)
        return r.height
    
    def set_zoomlevel(self, absolute=None, change=None):
        """
        Set zoomlevel of all child widgets.
        
        Keyword arguments:
        absolute -- Set zoomlevel to absolute level (should be between 0.2 and 3.0)
        change -- Alter zoomlevel by this value. It's ignored, if 'absolute' was given.
        """
        if absolute:
            self.zoomlevel = absolute
        elif change:
            self.zoomlevel += change
        self.zoomlevel = min(max(self.zoomlevel, 0.2),3)
        self.do_size_allocate(self.get_allocation())
