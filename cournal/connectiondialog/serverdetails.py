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

from gi.repository import Gtk, GObject
from twisted.internet.defer import Deferred

from cournal.connectiondialog.serverportentry import ServerPortEntry
from cournal.network import network

class ServerDetails(Gtk.Box):
    """
    Widget asking the user about the details (hostname and port) of the server
    he wishes to connect to.
    Note that currently the setup of the connection itself is also handled by
    this widget. A patch that seperates the functionality from the widget would
    be greatly appreciated
    """
    __gsignals__ = {
        "connecting": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str, int,)),
        "connected": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        "connection_failed": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    def __init__(self, dialog, builder):
        """
        Constructor
        
        Position arguments:
        dialog -- The parent GtkDialog widget.
        builder -- A builder object, which contains a "grid_server_details" object.
        """
        Gtk.Box.__init__(self)
        self.dialog = dialog
        self.deferred = None
        
        grid = builder.get_object("grid_server_details")
        self._server_entry = ServerPortEntry()
        
        self.add(grid)
        grid.attach(self._server_entry, 1, 1, 1, 1)
        
        self._server_entry.set_activates_default(True)
    
    def response(self, widget, response_id):
        """
        Called, when the user clicked on a button ('Connect' or 'Abort') or
        when the dialog is closed.
        If the user clicked on connect, we try to initiate the connection.
        
        Positional arguments:
        widget -- The widget, which triggered the response.
        response_id -- A Gtk.ResponseType indicating, which button the user pressed.
        """
        if response_id != Gtk.ResponseType.ACCEPT:
            self.dialog.destroy()
            return
        
        server = self._server_entry.server
        port = self._server_entry.port
        
        if port > 65535 or port < 0:
            self.dialog.error = _("The port must be below 65535")
            return
        
        if not self.dialog.parent.document.is_empty():
            if not self.confirm_clear_document():
               return
            self.dialog.parent.document.clear_pages()
            
        self.new_connection(server, port)
            
    def confirm_clear_document(self):
        """
        Ask the user, if he wishes to loose all changes he made to the current
        document, when he connects to a server.
        """
        message = Gtk.MessageDialog(self.dialog, (Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT), Gtk.MessageType.WARNING, Gtk.ButtonsType.YES_NO, _("Close current document?"))
        message.format_secondary_text(_("You will loose all changes to your current document, if you connect to a server. Continue without saving?"))
        message.set_title(_("Warning"))
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
        network.set_document(self.dialog.parent.document)
        d = network.connect(server, port)
        d.addCallbacks(self.on_connected, self.on_connection_failure)
        
        self.dialog.error = ""
        self.emit("connecting", server, port)
        return d
    
    def on_connected(self, perspective):
        """
        Called, when the connection to the server succeeded.
        """
        self.emit("connected")
    
    def on_connection_failure(self, reason):
        """
        Called, when the connection to the server failed. Display error message.
        """
        self.dialog.error = reason.getErrorMessage()
        self.emit("connection_failed")
