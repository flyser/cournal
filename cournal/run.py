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

from twisted.internet import reactor
from gi.repository import Gtk

from . import MainWindow

def run():
    """Start Cournal"""
    Gtk.IconTheme.get_default().prepend_search_path("./icons")
    
    window = MainWindow()
    window.connect("destroy", lambda _: reactor.stop())
    window.show_all()

    reactor.run() # aka Gtk.main()
