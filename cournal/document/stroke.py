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

import cairo

from twisted.spread import pb

class Stroke(pb.Copyable, pb.RemoteCopy):
    """
    A pen stroke on a layer, having a color, a linewidth and a list of coordinates
    
    If a stroke has variable width, self.coords contains tuples of three,
    else tuples of two floats.
    FIXME: don't ignore the variable width
    """
    def __init__(self, layer, color, linewidth, coords=None):
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
        try:
            if x > self.bound_min[0] and x < self.bound_max[0] and y > self.bound_min[1] and y < self.bound_max[1]:
                return True
            else:
                return False
        except:
            self.calculate_bounding_box()
            if x > self.bound_min[0] and x < self.bound_max[0] and y > self.bound_min[1] and y < self.bound_max[1]:
                return True
            else:
                return False

    def calculate_bounding_box(self, radius=5):
        """
        Calculate the bounding box of the stroke
        
        Keyword arguments:
        radius -- tolerance radius
        """
        
        bb_min_x = self.coords[0][0]
        bb_max_x = self.coords[0][0]
        bb_min_y = self.coords[0][1]
        bb_max_y = self.coords[0][1]
        for coord in self.coords[1:]:
            bb_min_x = min(bb_min_x, coord[0])
            bb_min_y = min(bb_min_y, coord[1])
            bb_max_x = max(bb_max_x, coord[0])
            bb_max_y = max(bb_max_y, coord[1])
        self.bound_min = [bb_min_x-radius, bb_min_y-radius]
        self.bound_max = [bb_max_x+radius, bb_max_y+radius]

    def getStateToCopy(self):
        """Gather state to send when I am serialized for a peer."""
        
        # d would be self.__dict__.copy()
        d = dict()
        d["color"] = self.color
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
        r, g, b, opacity = self.color
        
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        context.set_antialias(cairo.ANTIALIAS_GRAY)
        context.set_line_join(cairo.LINE_JOIN_ROUND)
        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_width(self.linewidth)
        
        first = self.coords[0]
        context.move_to(first[0], first[1])
        if len(self.coords) > 1:
            for coord in self.coords[1:]:
                context.line_to(coord[0], coord[1])
        else:
            context.line_to(first[0], first[1])
        x, y, x2, y2 = (a*scaling for a in context.stroke_extents())
        context.stroke()
        context.restore()
        
        return (x, y, x2, y2)

# Tell Twisted, that this class is allowed to be transmitted over the network.
pb.setUnjellyableForClass(Stroke, Stroke)
