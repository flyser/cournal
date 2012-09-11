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

_current_object = None
_current_coords = None
_start_point = None

def press(widget, event):
    """
    Mouse down event. Draw a point on the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _start_point, _current_coords, _current_object
    
    actualWidth = widget.get_allocation().width
    
    _current_object = Rect(widget.page.layers[0], primary.color, primary.fillcolor, primary.linewidth, [])
    #_current_stroke = widget.page.new_unfinished_stroke(color=primary.color, linewidth=primary.linewidth)
    _current_coords = _current_object.coords

    _start_point = [event.x, event.y]
    _current_coords.append(event.x*widget.page.width/actualWidth)
    _current_coords.append(event.y*widget.page.width/actualWidth)
    
    #widget.page.layers[0].obj.append(_current_stroke)

def motion(widget, event):
    pass

def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _start_point, _current_coords, _current_object
    r, g, b, opacity = primary.fillcolor
    actualWidth = widget.get_allocation().width

    context = cairo.Context(widget.backbuffer)
    
    # Fill rect
    context.move_to(_start_point[0], _start_point[1])
    context.line_to(_start_point[0], event.y)
    context.line_to(event.x, event.y)
    context.line_to(event.x, _start_point[1])
    context.close_path()
    
    context.set_source_rgba(r/255, g/255, b/255, opacity/255)
    context.set_antialias(cairo.ANTIALIAS_GRAY)
    context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
    x, y, x2, y2 = context.stroke_extents()
    context.fill()
    
    # Draw border
    context.move_to(_start_point[0], _start_point[1])
    context.line_to(_start_point[0], event.y)
    context.line_to(event.x, event.y)
    context.line_to(event.x, _start_point[1])
    context.close_path()
    
    r, g, b, opacity = primary.color
    context.set_source_rgba(r/255, g/255, b/255, opacity/255)
    context.stroke()
    
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)

    #_current_coords.append([_last_point[0]*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth])
    _current_coords.append(event.x*widget.page.width/actualWidth)
    _current_coords.append(event.y*widget.page.width/actualWidth)
    #_current_coords.append([event.x*widget.page.width/actualWidth, _last_point[1]*widget.page.width/actualWidth])
    #_current_coords.append([_last_point[0]*widget.page.width/actualWidth, _last_point[1]*widget.page.width/actualWidth])
    #widget.page.finish_stroke(_current_stroke)
    widget.page.new_obj(_current_object, send_to_network=True)
    history.register_draw_stroke(_current_object, widget.page)
    
    _start_point = None
    _current_coords = None
    _current_object = None
