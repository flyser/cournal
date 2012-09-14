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

def motion(widget, event):
    """
    Mouse motion event. Generate preview item and set render borders
    
    Positional arguments: see press()
    """
    global _last_point, _start_point, start_point_copy
    _end_point = [0,0]
    _start_point_copy[0]=_start_point[0]
    _start_point_copy[1]=_start_point[1]

    actualWidth = widget.get_allocation().width

    if _last_point:
        # Sort Coords
        if _last_point[0] < _start_point[0]:
            _end_point[0] = _start_point[0]
            _start_point[0] = _last_point[0]
        else:
            _end_point[0] = _last_point[0]

        if _last_point[1] < _start_point[1]:
            _end_point[1] = _start_point[1]
            _start_point[1] = _last_point[1]
        else:
            _end_point[1] = _last_point[1]
        center = [(_end_point[0] + _start_point[0]) / 2, (_end_point[1] + _start_point[1]) / 2]
        width = _end_point[0] - _start_point[0]
        height = _end_point[1] - _start_point[1]
        if height != 0 and width != 0:
            scale = (width + height) / 2
            scale_width = width / scale
            scale_height = height / scale
            context = cairo.Context(widget.backbuffer)
            context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
            # Draw Circle and scale it to oval
            context.translate(center[0], center[1])
            context.scale(scale_width / 2., scale_height / 2.)
            context.arc(0., 0., scale, 0., 2 * math.pi)
            context.scale(1 / (scale_width / 2.), 1 / (scale_height / 2.))
            context.translate(-center[0], -center[1])
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

    _start_point[0] = _start_point_copy[0]
    _start_point[1] = _start_point_copy[1]
            
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
    
    center = [(_end_point[0] + _start_point[0]) / 2, (_end_point[1] + _start_point[1]) / 2]
    width = _end_point[0] - _start_point[0]
    height = _end_point[1] - _start_point[1]
    if height == 0 or width == 0:
        widget.preview_item = None
    else:
        scale = (width + height) / 2
        scale_width = width / scale
        scale_height = height / scale
        context = cairo.Context(widget.backbuffer)
        context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
        # Draw Circle and scale it to oval
        context.translate(center[0], center[1])
        context.scale(scale_width / 2., scale_height / 2.)
        context.arc(0., 0., scale, 0., 2 * math.pi)
        context.scale(1 / (scale_width / 2.), 1 / (scale_height / 2.))
        context.translate(-center[0], -center[1])
        x, y, x2, y2 = context.stroke_extents()
        update_rect = Gdk.Rectangle()
        update_rect.x = x-2*primary.linewidth*actualWidth/widget.page.width
        update_rect.y = y-2*primary.linewidth*actualWidth/widget.page.width
        update_rect.width = x2-x+4*primary.linewidth*actualWidth/widget.page.width
        update_rect.height = y2-y+4*primary.linewidth*actualWidth/widget.page.width
        widget.get_window().invalidate_rect(update_rect, False)
        widget.preview_item = Circle(
            widget.page.layers[0],
            primary.color,
            primary.fill,
            primary.fillcolor,
            primary.linewidth,
            [center[0]*widget.page.width/actualWidth, center[1]*widget.page.width/actualWidth],
            [width/2*widget.page.width/actualWidth, height/2*widget.page.width/actualWidth, scale*widget.page.width/actualWidth])

    _start_point[0] = _start_point_copy[0]
    _start_point[1] = _start_point_copy[1]

def release(widget, event):
    """
    Mouse release event. Inform the corresponding Page instance, that the stroke
    is finished.
    
    This will cause the stroke to be sent to the server, if it is connected.
    
    Positional arguments: see press()
    """
    global _start_point
    widget.preview_item = None
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
    context.set_line_width(primary.linewidth*actualWidth/widget.page.width)
    # Draw Circle and scale it to oval
    context.translate(center[0], center[1])
    context.scale(scale_width / 2., scale_height / 2.)
    context.arc(0., 0., scale, 0., 2 * math.pi)
    context.scale(1 / (scale_width / 2.), 1 / (scale_height / 2.))
    context.translate(-center[0], -center[1])
    x, y, x2, y2 = context.stroke_extents()
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2*primary.linewidth*actualWidth/widget.page.width
    update_rect.y = y-2*primary.linewidth*actualWidth/widget.page.width
    update_rect.width = x2-x+4*primary.linewidth*actualWidth/widget.page.width
    update_rect.height = y2-y+4*primary.linewidth*actualWidth/widget.page.width
    widget.get_window().invalidate_rect(update_rect, False)
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
