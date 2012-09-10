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

import os, sys
import gettext
from io import StringIO
import string
import atexit
from tempfile import NamedTemporaryFile
import argparse
import pickle

from zope.interface import implementer

from twisted.cred import portal, checkers
from twisted.spread import pb
from twisted.internet import reactor
from twisted.internet.error import *
from twisted.python.failure import Failure

from cournal import __versionstring__ as cournal_version
from cournal.document.stroke import Stroke


# 0 - none
# 1 - minimal
# 2 - medium
# 3 - maximal
DEBUGLEVEL = 3

DEFAULT_AUTOSAVE_DIRECTORY = os.path.expanduser("~/.cournal")
DEFAULT_AUTOSAVE_INTERVAL = 60
DEFAULT_PORT = 6524
USERNAME = "test"
PASSWORD = "testpw"

# List of all characters that are allowed in filenames. Must not contain ; and :
valid_characters = string.ascii_letters + string.digits + ' _()+,.-=^~'

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
    def __init__(self, autosave_directory, autosave_interval):
        """
        Constructor.
        
        Test, if the autosave directory is writable and load saved data.
        
        Positional arguments:
        autosave_directory -- The directory within which to store the documents
        autosave_interval -- Interval in seconds within which to save the documents
        """
        self.documents = dict()
        self.autosave_directory = os.path.abspath(autosave_directory)
        self.autosave_interval = autosave_interval
        
        # Don't create the autosave directory, if autosaving is disabled
        if self.autosave_interval == 0:
            return
        
        if not os.path.isdir(self.autosave_directory):
            # Only create the autosave directory, if it wasn't changed by the user
            if self.autosave_directory != DEFAULT_AUTOSAVE_DIRECTORY:
                print(_("Autosave directory '{}' does not exist.").format(self.autosave_directory), file=sys.stderr)
                raise Exception()
            else:
                try:
                    os.mkdir(self.autosave_directory)
                except Exception as ex:
                    print(_("Could not create autosave directory: {}").format(self.autosave_directory, ex), file=sys.stderr)
                    raise ex
        os.chdir(self.autosave_directory)

        self.obtain_lockfile()
        
        # Load saved data
        for filename in [s for s in os.listdir() if s.endswith(".save") and s.startswith("cnl-")]:
            name = filename_to_docname(filename)
            with open(filename, "rb") as file:
                self.documents[name] = Document(name)
                self.documents[name].pages = pickle.load(file)
        
        debug(1, _("Loaded {} documents").format(len(self.documents)))
        
        reactor.callLater(self.autosave_interval, self.save_documents)
    
    def obtain_lockfile(self):
        """
        Try to obtain a lock file for the autosave directory to make sure,
        that we are the only ones writing there.
        """
        lockfile = self.autosave_directory + "/lock"
        if os.path.exists(lockfile):
            with open(lockfile, "rb") as f:
                pid = int(f.read())
            if self.is_pid_dead(pid):
                print(_(\
"""The autosave directory was locked by another instance of cournal-server,
that is not running anymore. This happens, when cournal-server crashed.
Make sure that no server is using the autosave directory '{}',
delete '{}' and try again.""").format(self.autosave_directory, lockfile), file=sys.stderr)
            else:
                print(_(\
"""The autosave directory is locked by another instance of cournal-server.
To run multiple instances concurrently, you need to set a different autosave directory and port."""), file=sys.stderr)
            sys.exit(-1)
        else:
            try:
                open(lockfile, 'w').write(str(os.getpid()))
            except Exception as ex:
                print(_("Could not create file in autosave directory: {}").format(ex), file=sys.stderr)
                raise ex
        self.lockfile = lockfile
    
    def release_lockfile(self):
        """Delete the lockfile created with obtain_lockfile()."""
        if self.lockfile:
            os.remove(self.lockfile)
    
    def is_pid_dead(self, pid):
        """Returns True, if no running program has the given PID."""
        try:
            # Signal 0 is no-op
            return os.kill(pid, 0)
        except OSError as e:
            #process is dead
            if e.errno == 3:
                return True
            #no permissions
            elif e.errno == 1:
                return False
            else:
                raise
    
    def exit(self):
        """
        The program is about to terminate. Save documents and release lockfile
        """
        if self.autosave_interval > 0:
            # Save on exit, if the user enabled autosave
            self.save_documents()
            # and release the directory lock
            self.release_lockfile()
    
    def save_documents(self):
        """
        Save all documents to files named "autosave_directory/documentname.save".
        
        The on-disk format is a pickled list of pages.
        """
        debug(3, _("Saving all documents."))
        for name, document in self.documents.items():
            if not document.has_unsaved_changes:
                continue
            # We write to a tmpfile and move it to the actual location to ensure
            # atomic writing of the file, meaning: In case of a crash, either the
            # old or the new version of that file is on the disk
            filename = docname_to_filename(name)
            tmpfile = NamedTemporaryFile(prefix=filename[:-5]+'-', suffix='.delete-me', dir=self.autosave_directory, mode='wb', delete=False)
            pickle.dump(document.pages, tmpfile, protocol=3)
            tmpfile.close()
            os.rename(tmpfile.name, self.autosave_directory + "/" + filename)
            document.has_unsaved_changes = False
        
        reactor.callLater(self.autosave_interval, self.save_documents)
        
    def get_document(self, documentname):
        """
        Returns a Document object given its name. If none with this name exists,
        it will be created.
        
        Positional arguments:
        documentname -- Name of the document you want to get
        """
        if documentname not in self.documents:
            if self.autosave_interval > 0:
                # Try to create a savefile, if it fails deny the document creation
                filename = docname_to_filename(documentname)
                try:
                    file = open(self.autosave_directory + "/" + filename, mode="wb")
                    pickle.dump([], file, protocol=3)
                    file.close()
                except Exception as ex:
                    return Failure(str(ex))
            self.documents[documentname] = Document(documentname)
            self.documents[documentname].has_unsaved_changes = True
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
        debug(1, _("New User connected: {}").format(name))
        self.name = name
        self.server = server
        self.remote = None
        self.documents = []
        
    def __del__(self):
        """Destructor. Called when the user disconnects."""
        debug(1, _("User disconnected: {}").format(self.name))
        
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
    
    def perspective_list_documents(self):
        """
        Return a list of all our documents.
        """
        debug(2, _("User {} requested document list").format(self.name))
        
        return list(self.server.documents.keys())

    def perspective_list_users(self, document):
        """
        Return a list of all our documents.
        """
        debug(2, _("User {} requested user list for {}").format(self.name), document)
        
        return list(self.server.documents.keys())

    
    def perspective_join_document(self, documentname):
        """
        Called by the user to join a document session.
        
        Positional arguments:
        documentname -- Name of the requested document session
        """
        debug(2, _("User {} started editing {}").format(self.name, documentname))
        
        document = self.server.get_document(documentname)
        if isinstance(document, Failure):
            return document
        document.add_user(self)
        self.documents.append(document)
        return document
    
    def perspective_ping(self):
        """Called by clients to verify, that the connection is still up."""
        return True
        
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
        self.has_unsaved_changes = False
    
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
        self.broadcast_user_list()
    
    def remove_user(self, user):
        """
        Called, when a user stops editing this document. Remove him from list
        
        Positional arguments:
        user -- The concerning User object.
        """
        self.users.remove(user)
        self.broadcast_user_list()
        
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
    
    def broadcast_user_list(self):
        """
        Broadcast user list to all clients.
        """
        user_names = []
        for u in self.users:
            user_names.append(u.name)
        for u in self.users:
            u.call_remote("user_list", user_names)        
    
    def view_list_users(self, from_user):
        """
        Send user name list to clients
        
        Positional arguments:
        from_user -- user that sent the request
        """
        user_names = []
        for u in self.users:
            user_names.append(u.name)
        #from_user.call_remote("user_list", user_names)
        return user_names
    
    def view_new_stroke(self, from_user, pagenum, stroke):
        """
        Broadcast the stroke received from one to all other clients.
        Called by clients to add a new stroke.
        
        Positional arguments:
        from_user -- The User object of the initiiating user.
        pagenum -- Page number the new stroke.
        stroke -- The new stroke
        """
        self.has_unsaved_changes = True
        
        while len(self.pages) <= pagenum:
            self.pages.append(Page())
        self.pages[pagenum].strokes.append(stroke)
        
        debug(3, _("New stroke on page {}").format(pagenum + 1))
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
        self.has_unsaved_changes = True
        
        for stroke in self.pages[pagenum].strokes:
            if stroke.coords == coords:
                self.pages[pagenum].strokes.remove(stroke)
                
                debug(3, _("Deleted stroke on page {}").format(pagenum + 1))
                self.broadcast("delete_stroke_with_coords", pagenum, coords, except_user=from_user)

class CmdlineParser():
    """
    Parse commandline options. Results are available as attributes of this class
    """
    def __init__(self):
        """Constructor. All variables initialized here are public."""
        self.port = DEFAULT_PORT
        self.autosave_directory = DEFAULT_AUTOSAVE_DIRECTORY
        self.autosave_interval = DEFAULT_AUTOSAVE_INTERVAL
        
    def parse(self):
        """
        Parse commandline options.
        """
        parser = argparse.ArgumentParser(description=_("Server for Cournal."),
                                         epilog=_("e.g.: %(prog)s -p port"))
        parser.add_argument("-p", "--port", nargs=1, type=int, default=[self.port],
                            help=_("Port to listen on"))
        parser.add_argument("-s", "--autosave-directory", nargs=1, default=[self.autosave_directory],
                            help=_("The directory within which to store the documents on the server."))
        parser.add_argument("-i", "--autosave-interval", nargs=1, type=int, default=[self.autosave_interval],
                            help=_("Interval in seconds within which to save modified documents to permanent storage. Set to 0 to disable autosave."))
        parser.add_argument("-v", "--version", action="version",
                            version="%(prog)s " + cournal_version)
        args = parser.parse_args()
        
        self.port = args.port[0]
        self.autosave_directory = args.autosave_directory[0]
        self.autosave_interval = args.autosave_interval[0]
        return self

def filename_to_docname(filename):
    """
    Convert the filename of a saved document to a documentname. Filenames have the
    form "cnl-[documentname].save" where [documentname] is the name of the
    document with escaped special characters
    
    Positional arguments:
    filename -- Name of the file with escaped special characters
    
    Return value: Name of the document without escaped special characters.
    """
    result = ""
    input = StringIO(filename[4:-5])
    
    while True:
        char = input.read(1)
        if char == "":
            break
        elif char == ':':
            charcode = ""
            while len(charcode) == 0 or charcode[-1] != ';':
                charcode += input.read(1)
            char = chr(int(charcode[:-1], 16))
        result += char
    
    return result

def docname_to_filename(name):
    """
    Convert the name of a document to a valid filename. Filenames have the
    form "cnl-[documentname].save" where [documentname] is the name of the
    document with escaped special characters.
    
    Positional arguments:
    name -- Name of the document without escaped special characters.
    
    Return value: Name of the file with escaped special characters
    """
    result = ""

    for char in name:
        if char in valid_characters:
            result += char
        else:
            result += ":" + hex(ord(char))[2:] + ";"

    return "cnl-" + result + ".save"

def main():
    """Start a Cournal server"""
    locale_dir = os.path.join(sys.prefix, "local",  "share", "locale")
    #locale_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
    gettext.install("cournal") #, locale_dir)

    args = CmdlineParser().parse()
    port = args.port
    
    realm = CournalRealm()
    realm.server = CournalServer(args.autosave_directory, args.autosave_interval)
    atexit.register(realm.server.exit)
    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(USERNAME, PASSWORD)
    p = portal.Portal(realm, [checker])
    
    try:
        reactor.listenTCP(port, pb.PBServerFactory(p))
    except CannotListenError as err:
        debug(0, _("ERROR: Failed to listen on port {}").format(err.port))
        return 1
    debug(2, _("Listening on port {}").format(port))

    reactor.run()

def debug(level, *args):
    """Helper function for debug output"""
    if level <= DEBUGLEVEL:
        print(*args)
