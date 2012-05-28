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

from math import sqrt
import cairo
from gi.repository import Gdk

from ... import network

THICKNESS = 5

def press(widget, event):
    _delete_strokes_near(widget, event.x, event.y)

def motion(widget, event):
    _delete_strokes_near(widget, event.x, event.y)

def release(widget, event):
    _active = False

def _delete_strokes_near(widget, x, y):
    factor = widget.page.width / widget.get_allocation().width
    x *= factor
    y *= factor
    
    for stroke in widget.page.strokes:
        for i in range(int(len(stroke)), 2):
            s_x = stroke[i]
            s_y = stroke[i+1]
            if sqrt((s_x-x)**2 + (s_y-y)**2) < THICKNESS:
                if network.is_connected:
                    network.local_delete_stroke(widget.page.number, stroke)

                widget.backbuffer_valid = False
                #FIXME: calculate stroke extents to improve performance :-)
                widget.get_window().invalidate_rect(None, False)

                #FIXME: Does this work reliably? Deleting items while iterating.
                widget.page.strokes.remove(stroke)
                break
