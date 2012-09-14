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
A pen tool. Draws a stroke with a certain color and size.
"""

_last_point = None
_current_coords = None
_current_stroke = None
linewidth = 1.5
color = (0,0,128,255)

def press(widget, event):
    """
    Mouse down event. Draw a point on the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _last_point, _current_coords, _current_stroke, linewidth, color
    
    _current_stroke = widget.page.new_unfinished_stroke(color=color, linewidth=linewidth)
    _current_coords = _current_stroke.coords
    widget.preview_item = _current_stroke

    _last_point = [event.x, event.y]
    motion(widget, event)
    
    widget.page.layers[0].strokes.append(_current_stroke)

def motion(widget, event):
    """
    Mouse motion event. Draw a line from the last to the new pointer location.
    
    Positional arguments: see press()
    """
    global _last_point, _current_coords
    
    update_rect = Gdk.Rectangle()
    scaling = widget.backbuffer.get_width()/widget.page.width

    x = min(_last_point[0], event.x) - linewidth*scaling/2
    y = min(_last_point[1], event.y) - linewidth*scaling/2
    x2 = max(_last_point[0], event.x) + linewidth*scaling/2
    y2 = max(_last_point[1], event.y) + linewidth*scaling/2
        
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)
    
    _last_point = [event.x, event.y]
    _current_coords.append([event.x/scaling, event.y/scaling])

def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _last_point, _current_coords, _current_stroke
    widget.page.finish_stroke(_current_stroke)
    widget.preview_item = None

    context = cairo.Context(widget.backbuffer)
    scaling = widget.backbuffer.get_width() / widget.page.width
    context.scale(scaling, scaling)
    _current_stroke.draw(context, scaling)
        
    _last_point = None
    _current_coords = None
    _current_stroke = None
