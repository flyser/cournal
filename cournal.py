#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cournal: A collaborative note taking and journal application with a stylus.
# Copyright (C) 2012 Fabian Henze
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

from gi.repository import Gtk
from twisted.internet import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from cournal import Document, MainWindow, Network

def main():
    network = Network()
    document = Document(sys.argv[1], network)
    network.connect()
    
    window = MainWindow(document, title="Cournal")
    window.connect("destroy", lambda _: reactor.stop())
    window.show_all()

    reactor.run() # aka Gtk.main()
    
if __name__ == "__main__":
    sys.exit(main())
