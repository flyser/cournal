#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of Cournal.
# Copyright (C) 2012 Simon Vetter
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

def set_pdf(pdf):
    """
    Set the pdf to be searched through.
    
    Positional arguments:
    pdf -- pdf poppler document
    """
    global _pdf, _found, _position, _page
    _pdf = pdf
    reset()
    
def get_last_result_page():
    """
    Get the page, where the last result was found on
    """
    if _position < len(_found):
        return _page
    return -1

def search(search_text):
    """
    Search text in document
    
    Positional arguments:
    search_text -- String to be searched
    """
    global _found, _position, _page
    
    _position += 1
    if _position < len(_found):
        return _page, _found[_position]
    else:
        _position = 0
        for i in range(_pdf.get_n_pages()):
            _page += 1
            if _page >= _pdf.get_n_pages():
                _page = 0 
            _found = _pdf.get_page(_page).find_text(search_text)
            if _found:
                return _page, _found[_position]
    return -1, None

def reset():
    """
    Reset last search
    """
    global _found, _position, _page
    _position = 0
    _page = 0
    _found = []
    
def draw(context, page):
    """
    Render search result marker
    
    Positional arguments:
    context -- The cairo context to draw on
    page -- Page search text was found on
    """
    context.save()
    context.set_source_rgba(1, 1, 0.4, 0.5)
    context.move_to(page.search_marker[0], page.search_marker[1])
    context.line_to(page.search_marker[2], page.search_marker[1])
    context.line_to(page.search_marker[2], page.search_marker[3])
    context.line_to(page.search_marker[0], page.search_marker[3])
    context.close_path()
    context.fill()
    context.restore()
