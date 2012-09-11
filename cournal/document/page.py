
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

from cournal.document.layer import Layer
from cournal.document.stroke import Stroke
from cournal.network import network
from cournal.document import history

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
        self.search_marker = None
    
    def new_stroke(self, stroke, send_to_network=False):
        """
        Add a new stroke to this page and possibly send it to the server, if
        connected.
        
        Positional arguments:
        stroke -- The Stroke object, that will be added to this page
        
        Keyword arguments:
        send_to_network -- Set True, to send the stroke to the server
                           (defaults to False)
        """
        self.layers[0].strokes.append(stroke)
        stroke.calculate_bounding_box()
        stroke.layer = self.layers[0]
        if self.widget:
            self.widget.draw_remote_stroke(stroke)
        if send_to_network:
            network.new_stroke(self.number, stroke)
        
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
        history.register_draw_stroke(stroke, self)
        stroke.calculate_bounding_box()
        network.new_stroke(self.number, stroke)

    def delete_stroke_with_coords(self, coords):
        """
        Delete all strokes, which have exactly the same coordinates as given.
        
        Positional arguments
        coords -- The list of coordinates
        """
        for stroke in self.layers[0].strokes[:]:
            if stroke.coords == coords:
                self.delete_stroke(stroke, send_to_network=False)
    
    def delete_stroke(self, stroke, send_to_network=False, register_in_history=True):
        """
        Delete a stroke on this page and possibly send this request to the server,
        if connected.
        
        Positional arguments:
        stroke -- The Stroke object, that will be deleted.
        
        Keyword arguments:
        send_to_network -- Set to True, to send the request for deletion the server
                           (defaults to False)
        register_in_history -- Make this command undoable
        """
        self.layers[0].strokes.remove(stroke)
        if self.widget:
            self.widget.delete_remote_stroke(stroke)
        if send_to_network:
            network.delete_stroke_with_coords(self.number, stroke.coords)
            if register_in_history:
                history.register_delete_stroke(stroke, self)
    
    def get_strokes_near(self, x, y, radius):
        """
        Finds strokes near a given point
        
        Positional arguments:
        x -- x coordinate of the given point
        y -- y coordinate of the given point
        radius -- Radius in pt, which influences the decision of what is considered "near"
        
        Return value: Generator for a list of all strokes, which are near that point
        """
        for stroke in self.layers[0].strokes[:]:
            if stroke.in_bounds(x, y):
                for coord in stroke.coords:
                    s_x = coord[0]
                    s_y = coord[1]
                    if ((s_x-x)**2 + (s_y-y)**2) < radius**2:
                        yield stroke
                        break
