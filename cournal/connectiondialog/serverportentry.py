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

from gi.repository import Gtk, Gdk

class ServerPortEntry(Gtk.EventBox):
    """
    A Gtk.Entry-like widget with one field for a hostname and one for a port.
    """
    def __init__(self, **args):
        """
        Constructor.
        
        Keyword arguments:
        **args -- Arguments passed to the Gtk.EventBox constructor
        """
        Gtk.EventBox.__init__(self, **args)
        
        frame = Gtk.Frame()
        server_port_align = Gtk.Box()
        self.server_entry = Gtk.Entry()
        colon_label = Gtk.Label()
        self.port_entry = Gtk.Entry()
        
        self.add(frame)
        frame.add(server_port_align)
        server_port_align.pack_start(self.server_entry, True, True, 0)
        server_port_align.pack_start(colon_label, False, False, 0)
        server_port_align.pack_start(self.port_entry, False, False, 0)
        
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1,1,1,1))
        frame.set_shadow_type(Gtk.ShadowType.IN)
        
        self.server_entry.set_has_frame(False)
        self.server_entry.set_text("127.0.0.1")
        self.server_entry.set_width_chars(20)
        colon_label.set_text(":")
        self.port_entry.set_has_frame(False)
        self.port_entry.set_max_length(5)
        self.port_entry.set_width_chars(5)
        self.port_entry.set_text("6524")
        
        self.port_entry.connect("insert_text", self.port_entry_updated)
    
    def port_entry_updated(self, widget, text, length, position):
        """
        Prevent wrong input in the port entry.
        Called each time the user changed the content of the port entry.
        
        Positional arguments: (see GtkEditable "insert-text" documentation)
        widget -- The widget that was updated.
        text -- The text to append.
        length -- The length of the text in bytes, or -1.
        position -- Location of the position text will be inserted at.
        """
        if not text.isdigit():
            widget.emit_stop_by_name("insert_text")
    
    def set_activates_default(self, setting):
        """
        Pressing Enter in this widget will activate the default widget for the
        window containing this widget.
        
        In other words: If setting is True, pressing enter equals pressing "Connect"
        
        Positional Arguments:
        setting -- True, to activate default widget when pressing enter.
        """
        self.port_entry.set_activates_default(setting)
        self.server_entry.set_activates_default(setting)
    
    @property
    def server(self):
        """The hostname of the server given by the user"""
        return self.server_entry.get_text()
    
    @server.setter
    def server(self, value):
        self.server_entry.set_text(value)
    
    @property
    def port(self):
        """The portnumber given by the user"""
        return int(self.port_entry.get_text())
    
    @port.setter
    def port(self, value):
        self.port_entry.set_text(value)
