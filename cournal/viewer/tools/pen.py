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

from ... import network
from ...document import Stroke

_last_point = None
_current_coords = None

def press(widget, event):
    global _last_point, _current_coords
    actualWidth = widget.get_allocation().width
    
    current_stroke = Stroke(widget.page.layers[0], color=(0,0,102,255))
    _current_coords = current_stroke.coords

    _last_point = [event.x, event.y]
    motion(widget, event)
    
    widget.page.layers[0].strokes.append(current_stroke)

def motion(widget, event):
    global _last_point, _current_coords
    #print("\rMotion "+str((event.x,event.y))+"  ", end="")
    actualWidth = widget.get_allocation().width
    context = cairo.Context(widget.backbuffer)
    
    context.set_source_rgb(0, 0, 0.4)
    context.set_antialias(cairo.ANTIALIAS_GRAY)
    context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.set_line_width(1.5*actualWidth/widget.page.width)
    
    context.move_to(_last_point[0], _last_point[1])
    context.line_to(event.x, event.y)
    x, y, x2, y2 = context.stroke_extents()
    context.stroke()
    
    update_rect = Gdk.Rectangle()
    update_rect.x = x-2
    update_rect.y = y-2
    update_rect.width = x2-x+4
    update_rect.height = y2-y+4
    widget.get_window().invalidate_rect(update_rect, False)

    _last_point = [event.x, event.y]
    _current_coords.append([event.x*widget.page.width/actualWidth, event.y*widget.page.width/actualWidth])

def release(widget, event):
    global _last_point, _current_coords
    if network.is_connected:
        network.local_new_stroke(widget.page.number, _current_coords)
    
    _last_point = None
    _current_coords = None