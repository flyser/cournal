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

from gi.repository import Gtk

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, **args):
        Gtk.AboutDialog.__init__(self, **args)
        
        self.set_modal(False)    
        
        self.set_program_name("Cournal")
        self.set_copyright("© Fabian Henze")
        self.set_comments("A collaborative note taking and journal application using a stylus.")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_website("https://github.com/Flyser/cournal")
        self.set_authors(["Fabian Henze"])
        
    def response_cb(self, widget, response_id):
        self.destroy()

        if response_id == Gtk.ResponseType.ACCEPT:
            print("OK clicked")

    def run_nonblocking(self):
        self.connect('response', self.response_cb)
        self.show()

# For testing purposes:
if __name__ == "__main__":
    dialog = AboutDialog()
    dialog.run()