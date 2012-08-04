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
    """
    The About Dialog of Cournal.
    """
    def __init__(self, parent=None, **args):
        """
        Constructor.
        
        Keyword arguments:
        parent -- Parent window of this dialog (defaults to no parent)
        **args -- Arguments passed to the Gtk.AboutDialog constructor
        """
        Gtk.AboutDialog.__init__(self, **args)
        
        self.set_modal(False)    
        self.set_transient_for(parent)
        
        self.set_program_name(_("Cournal"))
        self.set_logo_icon_name("cournal")
        self.set_copyright(_("©") + " Fabian Henze")
        self.set_comments(_("A collaborative note taking and journal application using a stylus."))
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_website("http://cournal-project.org")
        self.set_authors(["Fabian Henze", "Simon Vetter", "Martin Grohmann"])
        self.set_artists(["Simon Vetter"])
        self.set_translator_credits(_("translator-credits"))
        
    def run_nonblocking(self):
        """Run the dialog asynchronously, reusing the mainloop of the parent."""
        self.connect('response', lambda a,b: self.destroy())
        self.show()

# For testing purposes:
if __name__ == "__main__":
    dialog = AboutDialog()
    dialog.run()
