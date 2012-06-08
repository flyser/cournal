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

from . import Layer, Stroke
from .. import network

class Page:
    def __init__(self, document, pdf, number, layers=None):
        self.document = document
        self.pdf = pdf
        self.number = number
        self.layers = layers
        if self.layers is None:
            self.layers = [Layer(self, 0)]
        
        self.widget = None
        self.width, self.height = pdf.get_size()
    
    def new_stroke(self, stroke, send_to_network=False):
        self.layers[0].strokes.append(stroke)
        stroke.layer = self.layers[0]
        if self.widget:
            self.widget.draw_remote_stroke(stroke)
        if send_to_network:
            network.new_stroke(self.number, stroke)
        
    def new_unfinished_stroke(self, color, linewidth):
        return Stroke(layer=self.layers[0], color=color, linewidth=linewidth, coords=[])
    
    def finish_stroke(self, stroke):
        #TODO: rerender portion of screen.
        network.new_stroke(self.number, stroke)

    def delete_stroke_with_coords(self, coords):
        for stroke in self.layers[0].strokes[:]:
            if stroke.coords == coords:
                self.delete_stroke(stroke, send_to_network=False)
    
    def delete_stroke(self, stroke, send_to_network=False):
        self.layers[0].strokes.remove(stroke)
        if self.widget:
            self.widget.delete_remote_stroke(stroke)
        if send_to_network:
            network.delete_stroke_with_coords(self.number, stroke.coords)
    
    def get_strokes_near(self, x, y, radius):
        for stroke in self.layers[0].strokes[:]:
            for coord in stroke.coords:
                s_x = coord[0]
                s_y = coord[1]
                if sqrt((s_x-x)**2 + (s_y-y)**2) < radius:
                    yield stroke
                    break
