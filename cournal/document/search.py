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

#TODO:
# * "find next"
# * find the poppler search function

def set_pdf(pdf):
    """
    Set the pdf to be searched through.
    
    Positional arguments:
    pdf -- pdf poppler document
    """
    global _pdf
    _pdf = pdf
    _last_page = -1
    _last_pos = 0

def search(search_text, from_page = 0):
    """
    Search text in document
    
    Positional arguments:
    search_text -- String to be searched
    
    Keyword arguments:
    from_page = page to start search from
    """
    # Sadly, the poppler search function does not work in python :(
    # Thus, the page number is the most accurate we can return
    
    # Search from actual page
    for i in range(from_page, _pdf.get_n_pages()):
        if _pdf.get_page(i).get_text().find(search_text) > -1:
            return i
    # Start from beginning
    for i in range(from_page):
        if _pdf.get_page(i).get_text().find(search_text) > -1:
            return i
    return -1
    