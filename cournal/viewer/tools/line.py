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

"""
A line tool. Draws a straight line with a certain color and size.
"""

_start_point = None
_current_coords = None
_current_stroke = None
_last_point = None
from cournal.document.stroke import Stroke

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
    else:
        _last_point = [0,0]
    _last_point[0] = event.x
    _last_point[1] = event.y
    
    # Bounding Box for new line
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

    widget.preview_item = Stroke(
        widget.page.layers[0],
        primary.color,
        primary.linewidth,
        [[_start_point[0]*widget.page.width/actualWidth, _start_point[1]*widget.page.width/actualWidth],
        [event.x*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth]]
        )

def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _start_point, _current_coords, _current_stroke
    
    widget.preview_item = None
    
    r, g, b, opacity = primary.color
    actualWidth = widget.get_allocation().width
    context = cairo.Context(widget.backbuffer)
    
    context.set_source_rgba(r/255, g/255, b/255, opacity/255)
    context.set_antialias(cairo.ANTIALIAS_GRAY)
    context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
    
    context.move_to(_start_point[0], _start_point[1])
    context.line_to(event.x, event.y)
    x, y, x2, y2 = context.stroke_extents()
    context.stroke()
    
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)

    _current_coords.append([event.x*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth])

    widget.page.finish_stroke(_current_stroke)
    
    _start_point = None
    _current_coords = None
    _current_stroke = None
