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

from xojtools import Page as XojPage

from . import Layer

class Page(XojPage):
    def __init__(self, document, pdf, number, layers=None, width=-1, height=-1):
        width, height = pdf.get_size() # just overwrite given width and height
        XojPage.__init__(self, number=number, width=width, height=height)
        self.document = document
        self.pdf = pdf
        self.layers = layers
        if self.layers is None:
            self.layers = [Layer(self, 0)]
        
        self.new_stroke_callbacks = []
        self.delete_stroke_callbacks = []
            
    @classmethod
    def fromXojPage(cls, page, document, pdf):
        number = page.number
        layers = page.layers
        
        return cls(document, pdf, number, layers=layers)
    
    #FIXME: Move to layer
    def add_new_stroke_callback(self, callback):
        self.new_stroke_callbacks.append(callback)
       
    def add_delete_stroke_callback(self, callback):
        self.delete_stroke_callbacks.append(callback)

    def new_stroke_callback(self, stroke):
        self.layers[0].strokes.append(stroke)
        stroke.layer = self.layers[0]
        for callback in self.new_stroke_callbacks:
            callback(stroke)
       
    def delete_stroke_with_coords_callback(self, coords):
        for stroke in self.layers[0].strokes:
            if stroke.coords == coords:
                self.layers[0].strokes.remove(stroke)
                for callback in self.delete_stroke_callbacks:
                    callback(stroke)
