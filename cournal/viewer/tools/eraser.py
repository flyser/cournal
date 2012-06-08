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

THICKNESS = 6 # pt

def press(widget, event):
    _delete_strokes_near(widget, event.x, event.y)

def motion(widget, event):
    _delete_strokes_near(widget, event.x, event.y)

def release(widget, event):
    pass

def _delete_strokes_near(widget, x, y):
    scaling = widget.page.width / widget.get_allocation().width
    x *= scaling
    y *= scaling
    
    for stroke in widget.page.get_strokes_near(x, y, THICKNESS):
        widget.page.delete_stroke(stroke, send_to_network=True)
