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

class Layer:
    """
    A layer on a page, having a number and multiple objects.
    """
    def __init__(self, page, number, obj=None):
        """
        Constructor
        
        Positional arguments:
        page -- The Page object, which is the parent of this layer.
        number -- Layer number
        
        Keyword arguments:
        obj -- List of objects (defaults to [])
        """
        self.number = number
        self.page = page
        self.obj = obj
        
        if self.obj is None:
            self.obj = []
