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

USERNAME = "test"
PASSWORD = "testpw"

class Page:
    def __init__(self):
        self.strokes = []

class CournalServer:
    def __init__(self):
        # {documentname: Document()}
        self.documents = dict()

    def joinDocument(self, documentname, user):
        if documentname not in self.documents:
            self.documents[documentname] = Document(documentname)
        self.documents[documentname].addUser(user)
        return self.documents[documentname]

@implementer(portal.IRealm)
class CournalRealm:
    def requestAvatar(self, avatarID, mind, *interfaces):
        assert pb.IPerspective in interfaces
        avatar = User(avatarID)
        avatar.server = self.server
        avatar.attached(mind)
        return pb.IPerspective, avatar, lambda a=avatar:a.detached(mind)

class User(pb.Avatar):
    def __init__(self, name):
        debug(1, "New User connected:", name)
        self.name = name
        self.documents = list()
        
    def __del__(self):
        debug(1, "User disconnected:", self.name)
        
    def attached(self, mind):
        self.remote = mind
       
    def detached(self, mind):
        self.remote = None
        for document in self.documents:
            document.removeUser(self)

    def perspective_joinDocument(self, documentname):
        debug(2, "User", self.name, "started editing", documentname)
        
        document = self.server.joinDocument(documentname, self)
        self.documents.append(document)
        return document
        
    def send_stroke(self, method, pagenum, stroke):
        self.remote.callRemote(method, pagenum, stroke)

class Document(pb.Viewable):
    def __init__(self, documentname):
        self.name = documentname
        self.users = list()
        self.pages = []
        #self.pages[0].strokes.append([1.01, 20.1, 2.0, 10.0])
        #self.pages[0].strokes.append([2.01, 10.1, 3.0,  0.0])

    def addUser(self, user):
        self.users.append(user)
        for pagenum in range(len(self.pages)):
            for stroke in self.pages[pagenum].strokes:
                user.remote.callRemote("add_stroke", pagenum, stroke)
    
    def removeUser(self, user):
        self.users.remove(user)
        
    def broadcast(self, method, pagenum, stroke, except_user=None):
        for user in self.users:
            if user != except_user:
                user.send_stroke(method, pagenum, stroke)
    
    def view_new_stroke(self, from_user, pagenum, stroke):
        """
        Broadcast the stroke received from one to all other clients

        Called by clients to add a new stroke.
        """
        while len(self.pages) <= pagenum:
            self.pages.append(Page())
        self.pages[pagenum].strokes.append(stroke)
        
        debug(3, "New stroke on page", pagenum)
        self.broadcast("add_stroke", pagenum, stroke, except_user=from_user)
        
    def view_delete_stroke_with_coords(self, from_user, pagenum, coords):
        for stroke in self.pages[pagenum].strokes:
            if stroke.coords == coords:
                self.pages[pagenum].strokes.remove(stroke)
                
                debug(3, "Deleted stroke on page", pagenum)
                self.broadcast("delete_stroke_with_coords", pagenum, coords, except_user=from_user)

def debug(level, *args):
    if level <= DEBUGLEVEL:
        print(*args)

def main():
    realm = CournalRealm()
    realm.server = CournalServer()
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(USERNAME, PASSWORD)
    p = portal.Portal(realm, [checker])

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 6524

    try:
        reactor.listenTCP(port, pb.PBServerFactory(p))
    except CannotListenError as err:
        debug(0, "ERROR: Failed to listen on port", err.port)
        return 1
    
    debug(2, "Listening on port", port)
    reactor.run()

if __name__ == '__main__':
    sys.exit(main())
