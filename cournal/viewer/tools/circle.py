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
A pen tool. Draws a stroke with a certain color and size.
"""

_start_point = None

def press(widget, event):
    """
    Mouse down event. Draw a point on the pointer location.
    
    Positional arguments:
    widget -- The PageWidget, which triggered the event
    event -- The Gdk.Event, which stores the location of the pointer
    """
    global _start_point
    _start_point = [event.x, event.y]

def motion(widget, event):
    pass

def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _start_point
    _end_point = [0,0]
    actualWidth = widget.get_allocation().width
    
    # Sort Coords
    if event.x < _start_point[0]:
        _end_point[0] = _start_point[0]
        _start_point[0] = event.x
    else:
        _end_point[0] = event.x

    if event.y < _start_point[1]:
        _end_point[1] = _start_point[1]
        _start_point[1] = event.y
    else:
        _end_point[1] = event.y
    
    # Calculate center
    center = [(_end_point[0] + _start_point[0]) / 2, (_end_point[1] + _start_point[1]) / 2]
    
    # Calculate width and height
    width = _end_point[0] - _start_point[0]
    height = _end_point[1] - _start_point[1]

    # Stop it here if there's nothing to draw
    if height * width == 0:
        return

    scale = (width + height) / 2
    scale_width = width / scale
    scale_height = height / scale
    
    actualWidth = widget.get_allocation().width

    context = cairo.Context(widget.backbuffer)
    context.set_antialias(cairo.ANTIALIAS_GRAY)
    context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.set_line_width(primary.linewidth*actualWidth/widget.page.width)

    # Fill circle
    if primary.fill:
        r, g, b, opacity = primary.fillcolor
        context.set_source_rgba(r/255, g/255, b/255, opacity/255)
        # Draw Circle and scale it to oval
        context.translate(center[0], center[1])
        context.scale(scale_width / 2., scale_height / 2.)
        context.arc(0., 0., scale, 0., 2 * math.pi)
        context.scale(1 / (scale_width / 2.), 1 / (scale_height / 2.))
        context.translate(-center[0], -center[1])
        context.fill()
    
    # border
    r, g, b, opacity = primary.color
    context.set_source_rgba(r/255, g/255, b/255, opacity/255)
    i = 0
    context.move_to(center[0], center[1] + height/2)
    # We draw the border with strokes to keep konstant border width
    while i < (math.pi * 2):
        i += 0.1
        context.line_to(
            center[0] + math.sin(i)*width/2,
            center[1] + math.cos(i)*height/2)
    x, y, x2, y2 = context.stroke_extents()
    context.stroke()
    
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)

    #_current_coords.append([event.x*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth])

    #widget.page.finish_stroke(_current_stroke)
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
