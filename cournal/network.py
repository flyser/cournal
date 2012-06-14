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

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

USERNAME = "test"
PASSWORD = "testpw"

"""
Network communication via one instance of the _Network() class.
"""

class _Network(pb.Referenceable):
    """
    Network communication with Twisted Perspective Broker (RPC-like)
    """
    def __init__(self):
        """Constructor"""
        pb.Referenceable.__init__(self)
        self.document = None
        self.is_connected = False
    
    def set_document(self, document):
        """
        Associate this object with a document
        
        Positional arguments:
        document -- The Document object
        """
        self.document = document
        
    def connect(self, hostname, port):
        """
        Connect to a server
        
        Positional arguments:
        hostname -- The hostname of the server
        port -- The port to connect to
        """
        if self.document is None:
            return
        self.factory = pb.PBClientFactory()
        reactor.connectTCP(hostname, port, self.factory)
        
        d = self.factory.login(credentials.UsernamePassword(USERNAME, PASSWORD),
                               client=self)
        d.addCallbacks(self.connected, self.connection_failed)
        return d

    def connected(self, perspective):
        """
        Called, when the connection succeeded. Join a document now
        
        Positional arguments:
        perspective -- a reference to our user object
        """
        debug(1, "Connected")
        # This perspective is a reference to our User object.  Save a reference
        # to it here, otherwise it will get garbage collected after this call,
        # and the server will think we logged out.
        self.is_connected = True
        self.perspective = perspective
        d = perspective.callRemote("join_document", "document1")
        d.addCallbacks(self.got_server_document, callbackArgs=["document1"])
        
        return d

    def connection_failed(self, reason):
        """
        Called, when the connection could not be established.
        
        Positional arguments:
        reason -- A twisted Failure object with the reason the connection failed
        """
        debug(0, "Connection failed due to:", reason.getErrorMessage())
        self.is_connected = False
        
        return reason
        
    def got_server_document(self, server_document, name):
        """
        Called, when the server sent a reference to the remote document we requested
        
        Positional arguments:
        server_document -- remote reference to the document we are editing 
        name -- Name of the document
        """
        debug(2, "Started editing", name)
        self.server_document = server_document

    def remote_new_stroke(self, pagenum, stroke):
        """
        Called by the server, to inform us about a new stroke
        
        Positional arguments:
        pagenum -- On which page shall we add the stroke
        stroke -- The received Stroke object
        """
        if self.document and pagenum < len(self.document.pages):
            self.document.pages[pagenum].new_stroke(stroke)
    
    def new_stroke(self, pagenum, stroke):
        """
        Called by local code to send a new stroke to the server

        Positional arguments:
        pagenum -- On which page the stroke was added
        stroke -- The Stroke object to send
        """
        if self.is_connected:
            self.server_document.callRemote("new_stroke", pagenum, stroke)

    def remote_delete_stroke_with_coords(self, pagenum, coords):
        """
        Called by the server, when a remote user deleted a stroke
        
        Positional arguments:
        pagenum -- On which page the stroke was deleted
        coords -- The list of coordinates identifying a stroke
        """
        if self.document and pagenum < len(self.document.pages):
            self.document.pages[pagenum].delete_stroke_with_coords(coords)
    
    def delete_stroke_with_coords(self, pagenum, coords):
        """
        Called by local code to send a delete command to the server
        
        Positional arguments:
        pagenum -- On which page the stroke was deleted
        coords -- The list of coordinates identifying the stroke
        
        """
        if self.is_connected:
            self.server_document.callRemote("delete_stroke_with_coords", pagenum, coords)

# This is, what will be exported and included by other modules:
network = _Network()
        
def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print(*args)
