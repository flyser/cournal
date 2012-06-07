#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of xoj2tikz.
# Copyright (C) 2012 Fabian Henze
# 
# xoj2tikz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# xoj2tikz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with xoj2tikz.  If not, see <http://www.gnu.org/licenses/>.

class Stroke:
    """
    Stores information about a Xournal penstroke, possibly with variable width.
    
    A Stroke is created by the Xournal tools "pen", "highlighter" or "eraser".
    If a stroke has variable width, self.coords contains tuples of three
    else tuples of two floats.
    """
    def __init__(self, color=None, coords=None, width=0):
        """
        Constructor
        
        Keyword arguments:
        color -- Stroke color, tuple of red, green, blue and opacity (default (0,0,0,255))
        coords -- List of coordinates the stroke goes through (default [])
        width -- Width of the stroke in pt (default 0)
        """
        self.color = color
        self.coords = coords
        self.width = width
        if color is None:
            self.color = (0, 0, 0, 255)
        if coords is None:
            self.coords = []
        
    def __str__(self):
        return "Stroke with color '{}' and coords: {}"\
               .format(self.color, self.coords)

    def print(self, prefix=""):
        """
        Print a short description of the object.
        (for debugging purposes)
        
        Keyword arguments:
        prefix -- Prefix output with this string (default "")
        """
        print("{}Stroke with color '{}' and coords: {}"
              .format(prefix, self.color, self.coords))
