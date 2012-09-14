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
    Mouse down event. Set the start point for the rect
    
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
    
def motion(widget, event):
    """
    Mouse motion event. Generate preview item and set render borders
    
    Positional arguments: see press()
    """
    global _last_point

    if _last_point:
        # Bounding Box for last line
        actualWidth = widget.get_allocation().width
        context = cairo.Context(widget.backbuffer)
        context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
        context.move_to(_start_point[0], _start_point[1])
        context.line_to(_last_point[0], _last_point[1])
        x, y, x2, y2 = context.stroke_extents()
        update_rect = Gdk.Rectangle()
        update_rect.x = x-2*primary.linewidth*actualWidth/widget.page.width
        update_rect.y = y-2*primary.linewidth*actualWidth/widget.page.width
        update_rect.width = x2-x+4*primary.linewidth*actualWidth/widget.page.width
        update_rect.height = y2-y+4*primary.linewidth*actualWidth/widget.page.width
        widget.get_window().invalidate_rect(update_rect, False)
        widget.preview_item = Rect(
            widget.page.layers[0],
            primary.color,
            primary.fill,
            primary.fillcolor,
            primary.linewidth,
            [_start_point[0]*widget.page.width/actualWidth,
            _start_point[1]*widget.page.width/actualWidth,
            event.x*widget.page.width/actualWidth,
            event.y*widget.page.width/actualWidth]
            )
    else:
        _last_point = [0,0]
    _last_point[0] = event.x
    _last_point[1] = event.y

    actualWidth = widget.get_allocation().width
    context = cairo.Context(widget.backbuffer)
    context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
    context.move_to(_start_point[0], _start_point[1])
    context.line_to(event.x, event.y)
    x, y, x2, y2 = context.stroke_extents()
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2*primary.linewidth*actualWidth/widget.page.width
    update_rect.y = y-2*primary.linewidth*actualWidth/widget.page.width
    update_rect.width = x2-x+4*primary.linewidth*actualWidth/widget.page.width
    update_rect.height = y2-y+4*primary.linewidth*actualWidth/widget.page.width
    widget.get_window().invalidate_rect(update_rect, False)
    widget.preview_item = Rect(
        widget.page.layers[0],
        primary.color,
        primary.fill,
        primary.fillcolor,
        primary.linewidth,
        [_start_point[0]*widget.page.width/actualWidth,
        _start_point[1]*widget.page.width/actualWidth,
        event.x*widget.page.width/actualWidth,
        event.y*widget.page.width/actualWidth]
        )
        
def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """

    widget.preview_item = None

    global _start_point, _current_coords, _current_item
    actualWidth = widget.get_allocation().width

    _current_coords.append(event.x*widget.page.width/actualWidth)
    _current_coords.append(event.y*widget.page.width/actualWidth)
    widget.page.new_item(_current_item, send_to_network=True)
    history.register_draw_item(_current_item, widget.page)
    
    _start_point = None
    _current_coords = None
    _current_item = None
