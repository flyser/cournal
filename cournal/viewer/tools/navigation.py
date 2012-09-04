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
from gi.repository import Gdk

"""
A navigation tool.
"""

_vertical = None
_horizontal = None
_startpoint = None

def press(widget, event):
    """
    Mouse down event. Draw a point on the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _vertical, _horizontal, _startpoint
    
    _vertical = widget.parent.get_vadjustment()
    _horizontal = widget.parent.get_vadjustment()
    _startpoint = (event.x, event.y)

def motion(widget, event):
    """
    Mouse motion event. Draw a line from the last to the new pointer location.
    
    Positional arguments: see press()
    """
    global _vertical, _horizontal, _startpoint

    current = (event.x, event.y)
    _vertical.set_value(_vertical.get_value() + _startpoint[1] - current[1])

def release(widget, event):
    pass
