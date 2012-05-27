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

import gzip

def save_xoj_file(document, filename):
    pagenum = 1
    f = gzip.open(filename, "wb")
    
    # Thanks to Xournals awesome XML(-not)-parsing, we cant use elementtree here.
    # <t a="a" b="b"> is not the same as <t b="b" a="a"> ...
    
    r = "<?xml version=\"1.0\" standalone=\"no\"?>\n"
    r += "<xournal version=\"0.4.5\">\n"
    #r += "<!-- Created with Cournal -->\n"
    r += "<title>Xournal document - see http://math.mit.edu/~auroux/software/xournal/</title>\n"
    
    for p in document.pages:
        r += "<page width=\"" + str(round(p.width, 2)) + "\" height=\"" + str(round(p.height, 2)) + "\">\n"
        r += "<background type=\"pdf\""
        if pagenum == 1:
            r += " domain=\"absolute\" filename=\"" + document.filename + "\""
        r += " pageno=\"" + str(pagenum) + "\" />\n"
        pagenum += 1
        
        r += "<layer>\n"
        for s in p.strokes:
            r += "<stroke tool=\"pen\" color=\"#000066FF\" width=\"1.41\">\n"
            for coord in s:
                r += " " + str(round(coord, 2))
            if len(s) < 4:
                r += " " + str(s[0]) + " " + str(s[1])
            r += "\n</stroke>\n"
        r += "</layer>\n"
        r += "</page>\n"
    r += "</xournal>"
    
    f.write(bytes(r, "UTF-8"))
    f.close()
