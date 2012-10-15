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
from cournal.document.stroke import Stroke

"""
A line tool. Draws a straight line with a certain color and size.
"""

_start_point = None
_current_coords = None
_current_stroke = None
_last_point = None

def press(widget, event):
    """
    Mouse down event. Draw a point on the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _start_point, _current_coords, _current_stroke
    actualWidth = widget.get_allocation().width
    
    _current_stroke = widget.page.new_unfinished_stroke(color=primary.color, linewidth=primary.linewidth)
    _current_coords = _current_stroke.coords
    _current_coords.append([event.x*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth])

    _start_point = [event.x, event.y]
   
    widget.page.layers[0].items.append(_current_stroke)
    widget.preview_item = Stroke(
        primary.color,
        primary.linewidth,
        widget.page.layers[0],
        [[_start_point[0]*widget.page.width/actualWidth, _start_point[1]*widget.page.width/actualWidth],
        [_start_point[0]*widget.page.width/actualWidth, _start_point[1]*widget.page.width/actualWidth]]
        )
        
def motion(widget, event):
    """
    Mouse motion event. Update item and set render borders
    
    Positional arguments: see press()
    """
    global _last_point

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
        
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)
    widget.preview_item.coords[1] = [event.x/scaling, event.y/scaling]

def release(widget, event):
    """
    Mouse release event.
    
    This will cause the item to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """

    global _start_point, _current_coords, _current_stroke
    scaling = widget.backbuffer.get_width()/widget.page.width

    actualWidth = widget.get_allocation().width
    _current_coords.append([event.x/scaling, event.y/scaling])
    widget.page.finish_stroke(_current_stroke)

    context = cairo.Context(widget.backbuffer)
    context.scale(scaling, scaling)
    _current_stroke.draw(context, scaling)
    
    
    widget.preview_item = None
    _start_point = None
    _current_coords = None
    _current_stroke = None
