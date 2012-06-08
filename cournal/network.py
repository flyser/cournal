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

class Network(pb.Referenceable):
    def __init__(self):
        pb.Referenceable.__init__(self)
        self.document = None
        self.is_connected = False
    
    def set_document(self, document):
        self.document = document
        
    def connect(self, server, port):
        if self.document is None:
            return
        self.factory = pb.PBClientFactory()
        reactor.connectTCP(server, port, self.factory)
        
        d = self.factory.login(credentials.UsernamePassword(USERNAME, PASSWORD),
                               client=self)
        d.addCallbacks(self.connected, self.connection_failed)
        return d

    def connected(self, perspective):
        debug(1, "Connected")
        # This perspective is a reference to our User object.  Save a reference
        # to it here, otherwise it will get garbage collected after this call,
        # and the server will think we logged out.
        self.is_connected = True
        self.perspective = perspective
        d = perspective.callRemote("joinDocument", "document1")
        d.addCallbacks(self.got_server_document, callbackArgs=["document1"])
        
        return d

    def connection_failed(self, reason):
        debug(0, "Connection failed due to:", reason.getErrorMessage())
        self.is_connected = False
        
        return reason
        
    def got_server_document(self, server_document, name):
        debug(2, "Started editing", name)
        self.server_document = server_document

    def remote_new_stroke(self, pagenum, stroke):
        """Called by the server"""
        if self.document and pagenum < len(self.document.pages):
            self.document.pages[pagenum].new_stroke(stroke)
    
    def new_stroke(self, pagenum, stroke):
        """Called by local code"""
        if self.is_connected:
            self.server_document.callRemote("new_stroke", pagenum, stroke)

    def remote_delete_stroke_with_coords(self, pagenum, coords):
        """Called by the server"""
        if self.document and pagenum < len(self.document.pages):
            self.document.pages[pagenum].delete_stroke_with_coords(coords)
    
    def delete_stroke_with_coords(self, pagenum, coords):
        """Called by local code"""
        if self.is_connected:
            self.server_document.callRemote("delete_stroke_with_coords", pagenum, coords)

    def shutdown(self, result):
        reactor.stop()

# This is, what will be exported and included in other files:
network = Network()
        
def debug(level, *args):
    if level <= DEBUGLEVEL:
        print(*args)
