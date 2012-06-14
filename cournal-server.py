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

import sys
import argparse

from zope.interface import implementer

from twisted.cred import portal, checkers
from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.error import *

from cournal.document.stroke import Stroke

# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

VERSION = "0.2pre"
DEFAULT_PORT = 6524
USERNAME = "test"
PASSWORD = "testpw"

class Page:
    """
    A page in a document, having multiple strokes.
    """
    def __init__(self):
        self.strokes = []

class CournalServer:
    """
    The server object, that holds global state, which is shared between all users.
    """
    def __init__(self):
        self.documents = dict()

    def get_document(self, documentname):
        """
        Returns a Document object given its name. If none with this name exists,
        it will be created.
        
        Positional arguments:
        documentname -- Name of the document you want to get
        """
        if documentname not in self.documents:
            self.documents[documentname] = Document(documentname)
        return self.documents[documentname]

@implementer(portal.IRealm)
class CournalRealm:
    """
    The realm connects application-specific objects to the authentication system
    
    see: http://twistedmatrix.com/documents/current/api/twisted.cred.portal.IRealm.html
    """
    def requestAvatar(self, avatarID, mind, *interfaces):
        """
        Return a User object for a user (identified by its username), who just logged in.
        
        Positional arguments:
        avatarID -- string that identifies a user (in our case the username)
        mind -- Reference to the remote pb.Referencable object.
        *interfaces -- the interface(s) the returned avatar should implement
                       (in our case pb.IPerspective)
        """
        assert pb.IPerspective in interfaces
        user = User(avatarID, self.server)
        user.attached(mind)
        return pb.IPerspective, user, lambda a=user:a.detached(mind)

class User(pb.Avatar):
    """
    A remote user.
    """
    def __init__(self, name, server):
        """
        Constructor
        
        Positional arguments:
        name -- Name of the user
        server -- A CournalServer object 
        """
        debug(1, "New User connected:", name)
        self.name = name
        self.server = server
        self.remote = None
        self.documents = []
        
    def __del__(self):
        """Destructor. Called when the user disconnects."""
        debug(1, "User disconnected:", self.name)
        
    def attached(self, mind):
        """
        Called by twisted, when the corresponding User connects. In our case, the
        user object does not exist without a connected user.
        
        Positional arguments:
        mind -- Reference to the remote pb.Referencable object. used for .callRemote()
        """
        self.remote = mind
       
    def detached(self, mind):
        """
        Called by twisted, when the corresponding User disconnects. This object
        should be destroyed after this method terminated.
        
        Positional arguments:
        mind -- Reference to the remote pb.Referencable object.
        """
        self.remote = None
        for document in self.documents:
            document.remove_user(self)

    def perspective_join_document(self, documentname):
        """
        Called by the user to join a document session.
        
        Positional arguments:
        documentname -- Name of the requested document session
        """
        debug(2, "User", self.name, "started editing", documentname)
        
        document = self.server.get_document(documentname)
        document.add_user(self)
        self.documents.append(document)
        return document
        
    def call_remote(self, method, *args):
        """
        Call a remote method of this user.
        
        Positional arguments:
        method -- Name of the remote method
        *args -- Arguments of the remote method
        """

        self.remote.callRemote(method, *args)

class Document(pb.Viewable):
    """
    A Cournal document, having multiple pages.
    """
    def __init__(self, documentname):
        """
        Constructor
        
        Positional arguments:
        documentname -- Name of this document
        """
        self.name = documentname
        self.users = []
        self.pages = []

    def add_user(self, user):
        """
        Called, when a user starts editing this document. Send him all strokes
        that are currently in the document.
        
        Positional arguments:
        user -- The concerning User object.
        """
        self.users.append(user)
        for pagenum in range(len(self.pages)):
            for stroke in self.pages[pagenum].strokes:
                user.call_remote("new_stroke", pagenum, stroke)
    
    def remove_user(self, user):
        """
        Called, when a user stops editing this document. Remove him from list
        
        Positional arguments:
        user -- The concerning User object.
        """
        self.users.remove(user)
        
    def broadcast(self, method, *args, except_user=None):
        """
        Broadcast a method call to all clients
        
        Positional arguments:
        method -- Name of the remote method
        *args -- Arguments of the remote method
        
        Keyword arguments:
        except_user -- Don't broadcast to this user.
        """
        for user in self.users:
            if user != except_user:
                user.call_remote(method, *args)
    
    def view_new_stroke(self, from_user, pagenum, stroke):
        """
        Broadcast the stroke received from one to all other clients.
        Called by clients to add a new stroke.
        
        Positional arguments:
        from_user -- The User object of the initiiating user.
        pagenum -- Page number the new stroke.
        stroke -- The new stroke
        """
        while len(self.pages) <= pagenum:
            self.pages.append(Page())
        self.pages[pagenum].strokes.append(stroke)
        
        debug(3, "New stroke on page", pagenum+1)
        self.broadcast("new_stroke", pagenum, stroke, except_user=from_user)
        
    def view_delete_stroke_with_coords(self, from_user, pagenum, coords):
        """
        Broadcast the delete stroke command from one to all other clients.
        Called by Clients to delete a stroke.
        
        Positional arguments:
        from_user -- The User object of the initiiating user.
        pagenum -- Page number the deleted stroke
        coords -- The list coordinates of the deleted stroke
        """
        for stroke in self.pages[pagenum].strokes:
            if stroke.coords == coords:
                self.pages[pagenum].strokes.remove(stroke)
                
                debug(3, "Deleted stroke on page", pagenum+1)
                self.broadcast("delete_stroke_with_coords", pagenum, coords, except_user=from_user)

class CmdlineParser():
    """
    Parse commandline options. Results are available as attributes of this class
    """
    def __init__(self):
        """Constructor. All variables initialized here are public."""
        self.port = DEFAULT_PORT
        
    def parse(self):
        """
        Parse commandline options.
        """
        parser = argparse.ArgumentParser(description="Server for Cournal.",
                                         epilog="e.g.: %(prog)s -p port")
        parser.add_argument("-p", "--port", nargs=1, type=int, default=[DEFAULT_PORT],
                            help="Port to listen on")
        parser.add_argument("-v", "--version", action="version",
                            version="%(prog)s " + VERSION)
        args = parser.parse_args()
        
        self.port = args.port[0]
        return self

def main():
    """Start a Cournal server"""
    args = CmdlineParser().parse()
    port = args.port

    realm = CournalRealm()
    realm.server = CournalServer()
    checker = checkers.FilePasswordDB("passwddb")
    p = portal.Portal(realm, [checker])

    try:
        reactor.listenTCP(port, pb.PBServerFactory(p))
    except CannotListenError as err:
        debug(0, "ERROR: Failed to listen on port", err.port)
        return 1
    
    debug(2, "Listening on port", port)
    reactor.run()

def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print(*args)

if __name__ == '__main__':
    sys.exit(main())
