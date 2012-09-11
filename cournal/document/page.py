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

from cournal.document.layer import Layer
from cournal.document.stroke import Stroke
from cournal.document.rect import Rect
from cournal.network import network

class Page:
    """
    A page in a document, having a number and multiple layers.
    """
    def __init__(self, document, pdf, number, layers=None):
        """
        Constructor
        
        Positional arguments:
        document -- The Document object, which is the parent of this page.
        pdf -- A PopplerPage object
        number -- Page number
        
        Keyword arguments:
        layer -- List of Layer objects (defaults to a list of one Layer)
        """
        self.document = document
        self.pdf = pdf
        self.number = number
        self.layers = layers
        if self.layers is None:
            self.layers = [Layer(self, 0)]
        
        self.widget = None
        self.width, self.height = pdf.get_size()
    
    def new_obj(self, obj, send_to_network=False):
        """
        Add a new object to this page and possibly send it to the server, if
        connected.
        
        Positional arguments:
        obj -- The object, that will be added to this page
        
        Keyword arguments:
        send_to_network -- Set True, to send the object to the server
                           (defaults to False)
        """
        self.layers[0].obj.append(obj)
        obj.calculate_bounding_box()
        obj.layer = self.layers[0]
        if self.widget:
            self.widget.draw_remote_obj(obj)
        if send_to_network:
            network.new_obj(self.number, obj)

    def new_unfinished_stroke(self, color, linewidth):
        """
        Add a new empty stroke, which is not sent to the server, till
        finish_stroke() is called
        
        Positional arguments:
        color -- tuple of four: (red, green, blue, opacity)
        linewidth -- Line width in pt
        """
        return Stroke(layer=self.layers[0], color=color, linewidth=linewidth, coords=[])
    
    def finish_stroke(self, stroke):
        """
        Finish a stroke, that was created with new_unfinished_stroke() and
        send it to the server, if connected.
        
        Positional arguments:
        stroke -- The Stroke object, that was finished
        """
        #TODO: rerender that part of the screen.
        stroke.calculate_bounding_box()
        network.new_obj(self.number, stroke)

    def delete_objects_with_coords(self, coords):
        """
        Delete all objects, which have exactly the same coordinates as given.
        
        Positional arguments
        coords -- The list of coordinates
        """
        for obj in self.layers[0].obj[:]:
            if obj.coords == coords:
                self.delete_obj(obj, send_to_network=False)
    
    def delete_obj(self, obj, send_to_network=False):
        """
        Delete a object on this page and possibly send this request to the server,
        if connected.
        
        Positional arguments:
        obj -- The object, that will be deleted.
        
        Keyword arguments:
        send_to_network -- Set to True, to send the request for deletion the server
                           (defaults to False)
        """
        self.layers[0].obj.remove(obj)
        if self.widget:
            self.widget.delete_remote_obj(obj)
        if send_to_network:
            network.delete_objects_with_coords(self.number, obj.coords)
    
    def get_objects_near(self, x, y, radius):
        """
        Finds objects near a given point
        
        Positional arguments:
        x -- x coordinate of the given point
        y -- y coordinate of the given point
        radius -- Radius in pt, which influences the decision of what is considered "near"
        
        Return value: Generator for a list of all objects, which are near that point
        """
        for obj in self.layers[0].obj[:]:
            if obj.in_bounds(x, y):
                if isinstance(obj, Stroke):
                    for coord in obj.coords:
                        s_x = coord[0]
                        s_y = coord[1]
                        if ((s_x-x)**2 + (s_y-y)**2) < radius**2:
                            yield obj
                            break
                elif isinstance(obj, Rect):
                     yield obj
