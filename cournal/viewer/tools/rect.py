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
from cournal.document.rect import Rect
from cournal.document import history

_current_item = None
_current_coords = None
_start_point = None
_last_point = None

def press(widget, event):
    """
    Mouse down event. Set the start point for the item
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _start_point, _current_coords, _current_item
    
    actualWidth = widget.get_allocation().width
    
    _current_item = Rect(widget.page.layers[0], primary.color, primary.fill, primary.fillcolor, primary.linewidth, [])
    _current_coords = _current_item.coords

    _start_point = [event.x, event.y]
    _current_coords.append(event.x*widget.page.width/actualWidth)
    _current_coords.append(event.y*widget.page.width/actualWidth)
    widget.preview_item = Rect(
        widget.page.layers[0],
        primary.color,
        primary.fill,
        primary.fillcolor,
        primary.linewidth,
        [_start_point[0]*widget.page.width/actualWidth,
        _start_point[1]*widget.page.width/actualWidth,
        _start_point[0]*widget.page.width/actualWidth,
        _start_point[1]*widget.page.width/actualWidth]
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
    widget.preview_item.coords[2] = event.x/scaling
    widget.preview_item.coords[3] = event.y/scaling
        
def release(widget, event):
    """
    Mouse release event.
    
    This will cause the item to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """


    global _start_point, _current_coords, _current_item
    actualWidth = widget.get_allocation().width

    _current_coords.append(event.x*widget.page.width/actualWidth)
    _current_coords.append(event.y*widget.page.width/actualWidth)
    widget.page.new_item(_current_item, send_to_network=True)
    history.register_draw_item(_current_item, widget.page)
    
    widget.preview_item = None
    _start_point = None
    _current_coords = None
    _current_item = None
