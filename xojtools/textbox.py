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

class TextBox:
    """
    Stores information about a Xournal text box.
    
    A TextBox can have a font family, font size, coordinate of the upper
    left corner, text color and content.
    """
    def __init__(self, font="Sans", size=12.0, x=-1.0, y=-1.0, color=None,
                 text=""):
        """
        Constructor
        
        Keyword arguments:
        font -- Font family (default "Sans")
        size -- Font size in pt (default 12.0)
        x -- x coordinate of the TextBox in pt (default -1.0)
        y -- x coordinate of the TextBox in pt (default -1.0)
        color -- Text color, tuple of red, green, blue and opacity
                 (default (0,0,0,255))
        text -- Actual content of the TextBox (default "")
        """
        self.font = font
        self.size = size
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        if color is None:
            self.color = (0, 0, 0, 255)
    
    def __str__(self):
        return "TextBox \"{}\" in {} with size {} at ({},{}) and font '{}'"\
               .format(self.text, self.color, self.size, self.x, self.y,
                       self.font)
    
    def print(self, prefix=""):
        """
        Print a short description of the object.
        (for debugging purposes)
        
        Keyword arguments:
        prefix -- Prefix output with this string (default "")
        """
        print("{}TextBox \"{}\" in {} with size {} at ({},{}) and font '{}'"
              .format(prefix, self.text, self.color, self.size, self.x, self.y,
                      self.font))
