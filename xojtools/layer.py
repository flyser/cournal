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

class Layer:
    """
    Stores information about a Xournal Layer.
    
    A layer contains one or more items. An item can be a Stroke, Circle,
    TextBox, Rectangle, ...
    """
    def __init__(self, number=0, strokes=None):
        """
        Constructor
        
        Keyword arguments:
        number -- Layer number (default 0)
        strokes -- List of items, could be Stroke or TextBox objects for
                    example (default [])
        """
        self.number = number
        self.strokes = strokes
        if strokes is None:
            self.strokes = []

    def __str__(self):
        return "Layer " + str(self.number)

    def print(self, prefix=""):
        """
        Print a short description of the layer and all its items.
        (for debugging purposes)
        
        Keyword arguments:
        prefix -- Prefix output with this string (default "")
        """
        print(prefix + "Layer " + str(self.number) + ":")
        for item in self.strokes:
            item.print(prefix="  "+prefix)
