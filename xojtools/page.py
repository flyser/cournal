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

class Page:
    """
    Stores information of a Xournal page (e.g. list of layers, dimensions)
    
    A page contains one or more layers
    """
    def __init__(self, number=-1, layers=None, width=-1, height=-1):
        """
        Constructor
        
        Keyword arguments:
        number -- Page number (default -1)
        layers -- List of 'Layer' objects (default [])
        width -- 'Physical' width of the page in pt (default -1)
        height -- 'Physical' height of the page in pt (default -1)
        """
        self.number = number
        self.layers = layers
        self.width = width
        self.height = height
        if layers is None:
            self.layers = []
    
    def __str__(self):
        return "Page " + str(self.number)

    def print(self, prefix=""):
        """
        Print a short description of the page and all its layers.
        (mainly for debugging purposes)
        
        Keyword arguments:
        prefix -- Prefix output with this string (default "")
        """
        print(prefix = "Page " + str(self.number) + ":")
        for layer in self.layers:
            layer.print(prefix="  "+prefix)
