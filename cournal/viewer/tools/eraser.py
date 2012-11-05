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

"""
An eraser tool, that this deletes the complete item.
"""

THICKNESS = 6 # pt

def press(widget, event):
    """
    Mouse down event. Delete all item near the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    _delete_items_near(widget, event.x, event.y)

def motion(widget, event):
    """
    Mouse motion event. Delete all items near the pointer location.
    
    Positional arguments: see press()
    """
    _delete_items_near(widget, event.x, event.y)

def release(widget, event):
    """
    Mouse release event. Don't do anything, as the last motion event had the same
    location.
    
    Positional arguments: see press()
    """
    pass

def _delete_items_near(widget, x, y):
    """
    Delete all items near a given point.
    
    Positional arguments:
    widget -- The PageWidget to delete items on.
    x -- Delete item near this point (x coordinate on the widget (!))
    y -- Delete item near this point (y coordinate on the widget (!))
    """
    scaling = widget.page.width / widget.get_allocation().width
    x *= scaling
    y *= scaling
    
    for item in widget.page.get_items_near(x, y, THICKNESS):
        widget.page.delete_item(item, send_to_network=True)
