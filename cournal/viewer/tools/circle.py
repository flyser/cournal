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
from gi.repository import Gdk
from cournal.viewer.tools import primary
from cournal.document.circle import Circle
from cournal.document import history
import math

"""
A circle tool. Draws a circle with certain colors and radius.
"""

_start_point = None
_last_point = None
_start_point_copy = [0,0]

def press(widget, event):
    """
    Mouse down event. Keep the position
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _start_point
    _start_point = [event.x, event.y]
    scaling = widget.backbuffer.get_width()/widget.page.width
    widget.preview_item = Circle(
        widget.page.layers[0],
        primary.color,
        primary.fill,
        primary.fillcolor,
        primary.linewidth,
        [event.x/scaling ,event.y/scaling],
        [0,0,1])

def motion(widget, event):
    """
    Mouse motion event. Update item and set render borders
    
    Positional arguments: see press()
    """
    global _last_point, _preview_copy
    
    scaling = widget.backbuffer.get_width()/widget.page.width
    if _last_point:
        update_rect = Gdk.Rectangle()
        x = min(_last_point[0], _start_point[0]) - primary.linewidth*scaling/2
        y = min(_last_point[1], _start_point[1]) - primary.linewidth*scaling/2
        x2 = max(_last_point[0], _start_point[0]) + primary.linewidth*scaling/2
        y2 = max(_last_point[1], _start_point[1]) + primary.linewidth*scaling/2
        update_rect.x = x-2
        update_rect.y = y-2
        update_rect.width = x2-x+4
        update_rect.height = y2-y+4
        widget.get_window().invalidate_rect(update_rect, False)
    _last_point = [event.x, event.y]
    
    update_rect = Gdk.Rectangle()
    x = min(_start_point[0], event.x) - primary.linewidth*scaling/2
    y = min(_start_point[1], event.y) - primary.linewidth*scaling/2
    x2 = max(_start_point[0], event.x) + primary.linewidth*scaling/2
    y2 = max(_start_point[1], event.y) + primary.linewidth*scaling/2
    width = max(_start_point[0], event.x)-min(_start_point[0], event.x)
    height = max(_start_point[1], event.y)-min(_start_point[1], event.y)
    if width * height != 0:
        update_rect.x = x-2
        update_rect.y = y-2
        update_rect.width = x2-x+4
        update_rect.height = y2-y+4
        widget.get_window().invalidate_rect(update_rect, False)
        widget.preview_item.coords = [
            (x+x2)/scaling/2,
            (y+y2)/scaling/2]
        scale = (width + height) / 2
        widget.preview_item.scale = [
            width/scaling/2,
            height/scaling/2,
            scale/scaling
            ]
    else:
        widget.preview_item.scale = [0, 0, 1]
        
     
def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _start_point
    widget.preview_item = None
    actualWidth = widget.get_allocation().width
    
    # Sort Coords
    cx = min(_start_point[0], event.x)
    cy = min(_start_point[1], event.y)
    cx2 = max(_start_point[0], event.x)
    cy2 = max(_start_point[1], event.y)
    
    # Calculate center
    center = [(cx+cx2) / 2, (cy+cy2) / 2]
    
    # Calculate width and height
    width = cx2-cx
    height = cy2-cy

    # Stop it here if there's nothing to draw
    if height * width == 0:
        return

    scale = (width + height) / 2
    scale_width = width / scale
    scale_height = height / scale
    
    current_item = Circle(
        widget.page.layers[0],
        primary.color,
        primary.fill,
        primary.fillcolor,
        primary.linewidth,
        [center[0]*widget.page.width/actualWidth, center[1]*widget.page.width/actualWidth],
        [width/2*widget.page.width/actualWidth, height/2*widget.page.width/actualWidth, scale*widget.page.width/actualWidth])
    widget.page.new_item(current_item, send_to_network=True)
    history.register_draw_item(current_item, widget.page)
    
    _start_point = None
    
        