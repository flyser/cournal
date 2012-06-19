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
from . import network

class ConnectionDialog(Gtk.Dialog):
    """
    The "Connect to Server" dialog of Cournal.
    """
    def __init__(self, parent, **args):
        """
        Constructor.
        
        Positional arguments:
        parent -- Parent window of this dialog
        
        Keyword arguments:
        **args -- Arguments passed to the Gtk.Dialog constructor
        """
        Gtk.Dialog.__init__(self, **args)
        
        self.parent = parent
        
        builder = Gtk.Builder()
        builder.add_from_file("connection_dialog.glade")
        entry_grid = builder.get_object("grid_with_server_entry")
        self.server_entry = ServerPortEntry()
        self.multipage = builder.get_object("multipage")
        self.spinner = builder.get_object("spinner")
        self.error_label = builder.get_object("error_label")
        self.connecting_label = builder.get_object("connecting_label")
        
        self.get_content_area().add(builder.get_object("main_grid"))
        entry_grid.attach(self.server_entry, 1, 1, 1, 1)

        self.set_modal(False)
        self.set_has_resize_grip(False)
        self.set_resizable(False)
        self.set_title("Connect to Server")
        self.set_transient_for(parent)
        self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.add_button(Gtk.STOCK_CONNECT, Gtk.ResponseType.ACCEPT)
        self.set_default_response(Gtk.ResponseType.ACCEPT)
        self.server_entry.set_activates_default(True)
        
        self.show_all()
    
    def response(self, widget, response_id):
        """
        Called, when the user clicked on a button ('Connect' or 'Abort').
        Initiate a new connection or close the dialog.
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        if response_id != Gtk.ResponseType.ACCEPT:
            self.destroy()
            return
        
        server = self.server_entry.get_server()
        port = self.server_entry.get_port()
        
        if port > 65535 or port < 0:
            self.error_label.set_text("The port must be below 65535")
            self.error_label.show()
            return
        
        if not self.parent.document.is_empty():
            if not self.confirm_clear_document():
                return
            self.parent.document.clear_pages()
            
        self.new_connection(server, port)
            
    def confirm_clear_document(self):
        """
        Ask the user, if he wishes to loose all changes he made to the current
        document, when he connects to a server.
        """
        message = Gtk.MessageDialog(self, (Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT), Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, "Close current document?" )
        message.format_secondary_text("You will loose all changes to your current document, if you connect to a server. Continue without saving?")
        message.set_title("Warning")
        if message.run() != Gtk.ResponseType.YES:
            message.destroy()
            return False
        message.destroy()
        return True

    def new_connection(self, server, port):
        """
        Start to connect to a server and update UI accordingly.
        
        Positional arguments:
        server -- The hostname of the server to connect to.
        port -- The port on the server
        """
        network.set_document(self.parent.document)
        d = network.connect(server, port)
        d.addCallbacks(self.on_connected, self.on_connection_failure)
        
        self.multipage.set_current_page(1)
        self.spinner.start()
        self.error_label.set_text("")
        self.connecting_label.set_text("Connecting to {} ...".format(server))
        self.get_action_area().set_sensitive(False)
        
    def on_connected(self, perspective):
        """
        Called, when the connection to the server succeeded. Just close the dialog.
        """
        self.destroy()
    
    def on_connection_failure(self, reason):
        """
        Called, when the connection to the server failed. Display error message.
        """
        error = reason.getErrorMessage()

        self.multipage.set_current_page(0)
        self.spinner.stop()
        self.error_label.set_text(error)
        self.error_label.show()
        self.get_action_area().set_sensitive(True)

    def run_nonblocking(self):
        """Run the dialog asynchronously, reusing the mainloop of the parent."""
        self.connect('response', self.response)
        self.show()

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
            return
    
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
    
    def get_server(self):
        """Return the hostname of the server given by the user"""
        return self.server_entry.get_text()
    
    def get_port(self):
        """Return the portnumber given by the user"""
        return int(self.port_entry.get_text())

# For testing purposes:
if __name__ == "__main__":
    dialog = ConnectionDialog(None)
    dialog.run()
