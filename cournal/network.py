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

from time import time

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import credentials

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

PING_INTERVAL = 5
PING_TIMEOUT = 5

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
        self.window = None
        self.is_connected = False
        self.is_stalled = True
        self.last_data_received = 0
        self.watchdog = None
    
    def set_document(self, document):
        """
        Associate this object with a document.
        
        Positional arguments:
        document -- The Document object
        """
        self.document = document
        
    def set_window(self, window):
        """
        Associate this object with a Gtk window.
        
        Positional arguments:
        window -- The window object
        """
        self.window = window

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
        Called, when the connection succeeded. Initiate ping-pong timeout
        detection.
        
        Positional arguments:
        perspective -- a reference to our user object
        """
        debug(1, "Connected")
        # This perspective is a remote reference to our User object. Save it
        # here, otherwise it will get garbage collected at the end of this
        # function and the server will think we logged out.
        self.is_stalled = False
        self.is_connected = True
        self.perspective = perspective
        self.perspective.notifyOnDisconnect(self.disconnect_event)
        self.data_received()
        self.ping()
        self.window.connect_event()
    
    def connection_failed(self, reason):
        """
        Called, when the connection could not be established.
        
        Positional arguments:
        reason -- A twisted Failure object with the reason the connection failed
        """
        debug(0, "Connection failed due to:", reason.getErrorMessage())
        self.is_connected = False
        
        return reason
    
    def disconnect(self, _=None):
        """
        Disconnect from the server. Note that this will cancel ongoing operations.
        """
        if self.is_connected:
            self.perspective.broker.transport.loseConnection()
    
    def disconnect_event(self, event):
        """Called, when the client gets disconnected from the server."""
        self.is_connected = False
        self.connection_problems()
        if self.window:
            self.window.disconnect_event()
        
    def connection_problems(self):
        """
        Called when the server has not responded for some time or is disconnected.
        Inform the user, so he can decide, whether he wishes to disconnect or wait.
        """
        self.is_stalled = True
        if self.window:
            self.window.connection_problems()
        else:
            self.disconnect()
            
    def get_document_list(self):
        """
        Get a list of all documents the server knows about.
        
        Return value: A deferred, which fires when we got the list
        """
        d = self.perspective.callRemote("list_documents")
        d.addErrback(self.disconnect)
        return d
    
    def join_document_session(self, documentname):
        """
        Joins a "document editing session". This means, that we will automatically
        receive all strokes in this document (both preexisting and new ones).
        
        Positional arguments:
        documentname -- Name of the document you want to join
        
        Return value: A deferred, which fires when we got a reference to the document
        """
        d = self.perspective.callRemote("join_document", documentname)
        d.addCallbacks(self.got_server_document, self.disconnect, callbackArgs=[documentname])
        return d
    
    def got_server_document(self, server_document, name):
        """
        Called, when the server sent a reference to the remote document we requested
        
        Positional arguments:
        server_document -- remote reference to the document we are editing 
        name -- Name of the document
        """
        self.data_received()
        debug(2, "Started editing", name)
        self.server_document = server_document

    def remote_new_stroke(self, pagenum, stroke):
        """
        Called by the server, to inform us about a new stroke
        
        Positional arguments:
        pagenum -- On which page shall we add the stroke
        stroke -- The received Stroke object
        """
        self.data_received()
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
            d = self.server_document.callRemote("new_stroke", pagenum, stroke)
            d.addCallbacks(lambda x: self.data_received(), self.disconnect)

    def remote_delete_stroke_with_coords(self, pagenum, coords):
        """
        Called by the server, when a remote user deleted a stroke
        
        Positional arguments:
        pagenum -- On which page the stroke was deleted
        coords -- The list of coordinates identifying a stroke
        """
        self.data_received()
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
            d = self.server_document.callRemote("delete_stroke_with_coords", pagenum, coords)
            d.addCallback(lambda x,y: self.data_received(), self.disconnect)
    
    def ping(self):
        """
        Ping the server to verify, that we are still connected.
        """
        if self.is_connected:
            d = self.perspective.callRemote("ping")
            d.addCallbacks(self.ping_successful, self.disconnect)
        
    def ping_successful(self, r):
        """
        Called, when we receive a ping response from the server.
        """
        self.data_received()
        reactor.callLater(PING_INTERVAL, self.ping)
    
    def data_received(self):
        """
        Call this, when any kind of data is received from the server
        to get disconnect detection.
        
        A watchdog is set up, which triggers a disconnect, if we don't get
        a response from the server for some time.
        """
        self.is_stalled = False
        current_time = time()
        if current_time > 1 + self.last_data_received or current_time < self.last_data_received:
            self.last_data_received = current_time
            if self.watchdog and not self.watchdog.called:
                self.watchdog.cancel()
            self.watchdog = reactor.callLater(PING_INTERVAL + PING_TIMEOUT, self.connection_problems)
    
# This is, what will be exported and included by other modules:
network = _Network()
        
def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print(*args)
