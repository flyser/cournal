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

from twisted.internet import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor
from gi.repository import Gtk

from cournal.mainwindow import MainWindow

def run():
    """Start Cournal"""
    locale_dir = os.path.join(sys.prefix, "local",  "share", "locale")
    #locale_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
    gettext.install("cournal") #, locale_dir)
    
    Gtk.IconTheme.get_default().prepend_search_path("./icons")
    
    window = MainWindow()
    window.connect("destroy", lambda _: reactor.stop())
    window.show_all()

    reactor.run() # aka Gtk.main()
