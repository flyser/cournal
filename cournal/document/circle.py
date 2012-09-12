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
import math

from twisted.spread import pb

class Circle(pb.Copyable, pb.RemoteCopy):
    def __init__(self, layer, color, fill, fill_color, linewidth, coords, scale):
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
        self.fill = fill
        self.linewidth = linewidth
        self.coords = coords
        self.scale = scale
        
    def in_bounds(self, x, y):
        """
        Test if point is in bounding box of the stroke.
        
        Positional arguments:
        x, y -- point
        
        Returns:
        true, if point is in bounding box
        """
        radius = (self.coords[0] - x)**2 + (self.coords[1] - y)**2
        if radius < max(self.scale[0], self.scale[1])**2:
            # TODO Improve
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
        d["fill"] = self.fill
        d["coords"] = self.coords
        d["scale"] = self.scale
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

        if self.fill:
            r, g, b, opacity = self.fill_color
            context.set_source_rgba(r/255, g/255, b/255, opacity/255)
            # Draw Circle and scale it to oval
            context.translate(self.coords[0], self.coords[1])
            context.scale(self.scale[0]/self.scale[2], self.scale[1]/self.scale[2])
            context.arc(0., 0., self.scale[2], 0., 2 * math.pi)
            context.scale(1 / (self.scale[0]/self.scale[2]), 1 / (self.scale[1]/self.scale[2]))
            context.translate(-self.coords[0], -self.coords[1])
            context.fill()
        
        # Draw border
        i = 0
        context.move_to(self.coords[0], self.coords[1] + self.scale[1])
        # We draw the border with strokes to keep konstant border width
        while i < (math.pi * 2):
            i += 0.1
            context.line_to(
                self.coords[0] + math.sin(i)*self.scale[0],
                self.coords[1] + math.cos(i)*self.scale[1])

        r, g, b, opacity = self.color
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        
        x, y, x2, y2 = (a*scaling for a in context.stroke_extents())
        context.stroke()
        context.restore()
        
        return (x, y, x2, y2)

# Tell Twisted, that this class is allowed to be transmitted over the network.
pb.setUnjellyableForClass(Circle, Circle)
