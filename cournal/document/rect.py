#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Simon Vetter
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

import cairo

from twisted.spread import pb

class Rect(pb.Copyable, pb.RemoteCopy):
    def __init__(self, layer, color, fill_color, linewidth, coords=None):
        """
        Constructor
        
        Positional arguments:
        layer -- The Layer object, which is the parent of the stroke.
        color -- tuple of four: (red, green, blue, opacity)
        linewidth -- Line width in pt
        
        Keyword arguments:
        coords -- A list of coordinates (defaults to [])
        """
        self.layer = layer
        self.color = color
        self.fill_color = fill_color
        self.linewidth = linewidth
        self.coords = coords
        if self.coords is None:
            self.coords = []
    
    def in_bounds(self, x, y):
        """
        Test if point is in bounding box of the stroke.
        
        Positional arguments:
        x, y -- point
        
        Returns:
        true, if point is in bounding box
        """
        if self.coords[0] < self.coords[2]:
            s_x = self.coords[0]
            e_x = self.coords[2]
        else:
            s_x = self.coords[2]
            e_x = self.coords[0]
        if self.coords[1] < self.coords[3]:
            s_y = self.coords[1]
            e_y = self.coords[3]
        else:
            s_y = self.coords[3]
            e_y = self.coords[1]
        
        if x > s_x and x < e_x and y > s_y and y < e_y:
            return True
        else:
            return False

    def calculate_bounding_box(self, radius=5):
        pass
    
    def getStateToCopy(self):
        """Gather state to send when I am serialized for a peer."""
        
        # d would be self.__dict__.copy()
        d = dict()
        d["color"] = self.color
        d["fill_color"] = self.fill_color
        d["coords"] = self.coords
        d["linewidth"] = self.linewidth
        return d

    def draw(self, context, scaling=1):
        """
        Render this stroke
        
        Positional arguments:
        context -- The cairo context to draw on
        
        Keyword arguments:
        scaling -- scale the stroke by this factor (defaults to 1.0)
        """
        context.save()
        r, g, b, opacity = self.fill_color
        
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        context.set_antialias(cairo.ANTIALIAS_GRAY)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_width(self.linewidth)

        # Fill rect
        context.move_to(self.coords[0], self.coords[1])
        context.line_to(self.coords[0], self.coords[3])
        context.line_to(self.coords[2], self.coords[3])
        context.line_to(self.coords[2], self.coords[1])
        context.close_path()
        context.fill()
        
        # Draw border
        context.move_to(self.coords[0], self.coords[1])
        context.line_to(self.coords[0], self.coords[3])
        context.line_to(self.coords[2], self.coords[3])
        context.line_to(self.coords[2], self.coords[1])
        context.close_path()
        
        r, g, b, opacity = self.color
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        
        x, y, x2, y2 = (a*scaling for a in context.stroke_extents())
        context.stroke()
        context.restore()
        
        return (x, y, x2, y2)

# Tell Twisted, that this class is allowed to be transmitted over the network.
pb.setUnjellyableForClass(Rect, Rect)
