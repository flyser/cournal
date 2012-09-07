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

from cournal.network import network

class History:
    def __init__(self, menu_undo, menu_redo, tool_undo, tool_redo):
        self.menu_undo = menu_undo
        self.menu_redo = menu_redo
        self.tool_undo = tool_undo
        self.tool_redo = tool_redo
        self.undo_list=[]
        self.redo_list=[]
        
    def undo(self, menuitem):
        action = self.undo_list.pop()
        self.add_redo_action(action)
        action.undo()
        if len(self.undo_list) == 0:
            self.deactivate_undo()

    def redo(self, menuitem):
        action = self.redo_list.pop()
        self.add_undo_action(action, clear_redo=False)
        action.redo()
        if len(self.redo_list) == 0:
            self.deactivate_redo()

    def register_draw_stroke(self, stroke, page):
        self.add_undo_action(Action_draw_stroke(stroke, page))

    def register_delete_stroke(self, stroke, page):
        self.add_undo_action(Action_delete_stroke(stroke, page))

    def add_undo_action(self, action, clear_redo=True):
        self.undo_list.append(action)
        if len(self.undo_list) > 20:
            self.undo_list.pop(0)
        if len(self.undo_list) == 1:
            self.activate_undo()
        if clear_redo:
            self.deactivate_redo()
            self.redo_list = []

    def add_redo_action(self, action):
        self.redo_list.append(action)
        if len(self.redo_list) == 1:
            self.activate_redo()

    def deactivate_undo(self):
        self.menu_undo.set_sensitive(False)
        self.tool_undo.set_sensitive(False)

    def deactivate_redo(self):
        self.menu_redo.set_sensitive(False)
        self.tool_redo.set_sensitive(False)

    def activate_undo(self):
        self.menu_undo.set_sensitive(True)
        self.tool_undo.set_sensitive(True)

    def activate_redo(self):
        self.menu_redo.set_sensitive(True)
        self.tool_redo.set_sensitive(True)

class Action_draw_stroke:
    def __init__(self, stroke, page):
        self.stroke = stroke
        self.page = page
    
    def undo(self):
        self.page.delete_stroke(self.stroke, send_to_network=True, register=False)

    def redo(self):
        self.page.new_stroke(self.stroke, send_to_network=True)

class Action_delete_stroke:
    def __init__(self, stroke, page):
        self.stroke = stroke
        self.page = page
    
    def undo(self):
        self.page.new_stroke(self.stroke, send_to_network=True)

    def redo(self):
        self.page.delete_stroke(self.stroke, send_to_network=True, register=False)
       