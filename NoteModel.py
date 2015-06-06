'''
Created on 05/giu/2015

@author: koala
'''

initText = """Welcome to OGapp!

OGapp is a slim sized and fast program to manage your textual notes. Notes are organized in pages and it is possible to setup a main password to get the access to the notes. When the notes are password protected the .ogp file in which the notes are stored will be encrypted.
OGapp is cross platform and is available for Windows, Linux and (maybe in the future) Mac. It is based on Qt4 and is written in C++.

This software is OPEN SOURCE and released under GPL license so you can feel FREE to use, copy, share, (but above all) to study, analyze and modify it as you like (within the terms of the license).
If you like, hate or simply use this software, if you find any bug or have any request, please do not hesitate to let me know through the services offered by the site that hosts the project or through my Facebook page (http://facebook.com/koalakoker ). And (if you think it's the case) do not hesitate to recommend the program to your friends."""

import gtk
import gobject
import datetime
from undobufferrich import undobufferrich

class NoteModel(gtk.TreeStore):
    newPageID = 2 #default value 1 is the welcome screen
    
    def __init__(self, tagTable = None):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gtk.TextBuffer)
        #init treestore with the following types
        # 0: String - Title of the note
        # 1: Int - ID of the note (unique ID inside the db)
        # 2: String - Time stamp (Creation)
        # 3: String - Time stamp (Last modification) 
        # 4: String - Testo nota
        self.tagTable = tagTable
        
        self.hnd = self.connect("row-changed", self.callback)
         
    def callback(self, treemodel, path, piter):
        self.disconnect(self.hnd)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.set_value (piter, 3, now)
        self.hnd = self.connect("row-changed", self.callback)
        
    def populate(self):        
        for parent in range(4):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            it = ""
            if (parent == 0):
                it = initText
            self.disconnect(self.hnd)
            piter = self.append(None, ('parent %i' % parent, self.newPageID, now, now, undobufferrich(it, self.tagTable)))
            self.hnd = self.connect("row-changed", self.callback)
            self.newPageID += 1
            for child in range(3):
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                self.disconnect(self.hnd)
                self.append(piter, ('child %i of parent %i' % (child, parent), self.newPageID, now, now, undobufferrich("", self.tagTable)))
                self.hnd = self.connect("row-changed", self.callback)
                self.newPageID += 1
        
                
    def addNewNote(self, node = None):
        # return the iter to the new node
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.disconnect(self.hnd)
        piter = self.append(node, ('new note %i' % self.newPageID , self.newPageID, now, now, undobufferrich('', self.tagTable)))
        self.hnd = self.connect("row-changed", self.callback)
        self.newPageID += 1
        return piter
        
if __name__ == '__main__':
    note = NoteModel()
    note.populate()
    note.addNewNote()