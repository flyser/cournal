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

from gi.repository import Gtk

from .. import network

class ConnectingPage(Gtk.Box):
    """
    Simple widget showing just a spinner and a "Connecting ..." label
    """
    def __init__(self, dialog, builder):
        """
        Constructor
        
        Position arguments:
        dialog -- The parent GtkDialog widget.
        builder -- A builder object, which contains a "grid_connecting" object.
        """
        Gtk.Box.__init__(self)
        self.dialog = dialog
        self.deferred = None
        
        grid = builder.get_object("grid_connecting")
        self.connecting_label = builder.get_object("connecting_label")
        self.add(grid)
    
    def response(self, widget, response_id):
        """
        The buttons that could trigger a response have been disabled, but we
        receive a response, when the user closes the window
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        if response_id == Gtk.ResponseType.ACCEPT:
            print("This should never be called")
            return
        if self.deferred and not self.deferred.called:
            self.deferred.cancel()
            network.disconnect()
    
    @property
    def message(self):
        """The Message to display above the spinner widget"""
        return self.connecting_label.get_text()
    @message.setter
    def message(self, value):
        self.connecting_label.set_text(value)
