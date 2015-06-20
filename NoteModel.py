'''
Created on 05/giu/2015

@author: koala
'''

import XML
import TextBuffer2HTMLConvert

initText = """Welcome to OGapp!

OGapp is a slim sized and fast program to manage your textual notes. Notes are organized in pages and it is possible to setup a main password to get the access to the notes. When the notes are password protected the .ogp file in which the notes are stored will be encrypted.
OGapp is cross platform and is available for Windows, Linux and (maybe in the future) Mac. It is based on Qt4 and is written in C++.

This software is OPEN SOURCE and released under GPL license so you can feel FREE to use, copy, share, (but above all) to study, analyze and modify it as you like (within the terms of the license).
If you like, hate or simply use this software, if you find any bug or have any request, please do not hesitate to let me know through the services offered by the site that hosts the project or through my Facebook page (http://facebook.com/koalakoker ). And (if you think it's the case) do not hesitate to recommend the program to your friends."""

import gtk
import gobject
import datetime
from undobufferrich import undobufferrich

COL_Title = 0
COL_ID = 1
COL_Creation = 2
COL_Modify = 3
COL_Text = 4
COL_LinkList = 5

class NoteModel(gtk.TreeStore):
    newPageID = 2 #default value 1 is the welcome screen
    modified = True
    
    XML_DUMMY = -1
    XML_GTK_SERIALIZE = 0
    XML_HTML = 1
    
    xml_save_mode = XML_GTK_SERIALIZE
    
    XML_NOTE_TAG = "note"
    XML_TITLE_TAG = "Title"
    XML_ID_TAG = "ID"
    XML_CREATION_TAG = "CreationDate"
    XML_LASTMODIFY_TAG = "LastModify"
    XML_LINKLIST_TAG = "LinkList"
    
    XML_VER = "1.0"
    
    def __init__(self, tagTable = None):
        gtk.TreeStore.__init__(self, 
                               gobject.TYPE_STRING,   #0 
                               gobject.TYPE_INT,      #1
                               gobject.TYPE_STRING,   #2
                               gobject.TYPE_STRING,   #3 
                               gtk.TextBuffer,        #4
                               gobject.TYPE_STRING    #5
                               )
        #init treestore with the following types
        # 0: String - Title of the note
        # 1: Int - ID of the note (unique ID inside the db)
        # 2: String - Time stamp (Creation)
        # 3: String - Time stamp (Last modification) 
        # 4: String - Note text
        # 5: String - List of Links separated by '#' 
        self.tagTable = tagTable
        
        self.hnd = self.connect("row-changed", self.rowChangedCallback)
    
    def setModified(self, modified):
        self.modified = modified
        self.emit("modified_title")
         
    def rowChangedCallback(self, treemodel, path = None, piter = None):
        if (piter != None):
            self.disconnect(self.hnd)
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.set_value (piter, 3, now)
            self.setModified(True)
            self.hnd = self.connect("row-changed", self.rowChangedCallback)
        
    def populate(self):        
        for parent in range(4):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            it = ""
            if (parent == 0):
                it = initText
            self.disconnect(self.hnd)
            piter = self.append(None, ('parent %i' % parent, self.newPageID, now, now, self.CreateNewBuffer(it, self.tagTable),""))
            self.hnd = self.connect("row-changed", self.rowChangedCallback)
            self.newPageID += 1
            for child in range(3):
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                self.disconnect(self.hnd)
                self.append(piter, ('child %i of parent %i' % (child, parent), self.newPageID, now, now, self.CreateNewBuffer("", self.tagTable),""))
                self.hnd = self.connect("row-changed", self.rowChangedCallback)
                self.newPageID += 1
    
    def TextChanged(self, textBuffer):
        self.emit("modified_text")    
    
    def CreateNewBuffer(self, initText = "", tagTable = None, connect = True):
        newText = undobufferrich(initText, tagTable)
        if (connect):
            newText.connect("changed", self.TextChanged)
        return newText
    
    def CreateNewNote(self, node = None):
        # This function create a totally new note and return the iter to the new node
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.disconnect(self.hnd)
        piter = self.append(node, ('new note %i' % self.newPageID , self.newPageID, now, now, self.CreateNewBuffer('', self.tagTable),""))
        self.hnd = self.connect("row-changed", self.rowChangedCallback)
        self.setModified(True)
        self.newPageID += 1
        return piter
    
    def addNote(self, node, title, idNote, creation, modify, textbuffer, linkList):
        # This function add a note in the tree and return the iter to the node
        
        self.disconnect(self.hnd)
        piter = self.append(node, (title , idNote, creation, modify, textbuffer, linkList))
        self.hnd = self.connect("row-changed", self.rowChangedCallback)
        return piter
    
    def addLink(self, piter, noteID):
        # Add a new link to the noteID to the link list
        linkList = self.get_value(piter, COL_LinkList) 
        if (linkList == ""):
            separator = ""
        else:
            separator = "#"
        linkList += separator + str(noteID)
        self.set_value(piter, COL_LinkList, linkList)
        print (linkList)
    
    def save(self, filename = None):
        
        try:
            xml = XML.XML(self.XML_VER)
        
            piter = self.get_iter_root()
        
            if (piter != None):
                self.insertXMLEntry(piter, xml)
            
                xml.save(filename)
                self.setModified(False)
        except:
            return False
        return True
        
    def load(self, filename = None):
                        
        xml = XML.XML(self.XML_VER) # Dummy ver it is loaded from the file
        try:
            xml.load(filename)
        except:
            return False
        self.clear() 
        self.insertNoteEntry(None, xml.root) # Node = none is root
        self.setModified(False)
        return True
        
    # Save
    def insertXMLEntry(self, piter, xml, parent = None):
        # Recursive function to create an XML node from data coming from notes
        # piter is iterator of node model from where to get data
        # xml is the xml object to populate
        # parent is the parent node of the inserted xml element (None = root)
        # This function get text and attribute and add the new xml element, then
        # it re iterate for each child of piter, then
        # it re iterate for each item next (brother) of piter
        
        #Text
        if (self.xml_save_mode == self.XML_GTK_SERIALIZE):
            textNote = self.get_value(piter, COL_Text)
            text = TextBuffer2HTMLConvert.serialize(textNote)
        elif (self.xml_save_mode == self.XML_HTML):
            textNote = self.get_value(piter, COL_Text)
            text = TextBuffer2HTMLConvert.toHTML(textNote)
        elif (self.xml_save_mode == self.XML_DUMMY):
            text = "Dummy"
        else:
            return
        
        #Attributes
        title = self.get_value(piter, COL_Title)
        note_id = self.get_value(piter, COL_ID)
        creation = self.get_value(piter, COL_Creation)
        modify = self.get_value(piter, COL_Modify)
        linkList = self.get_value(piter, COL_LinkList)
        attr = { self.XML_TITLE_TAG : title,
                 self.XML_ID_TAG : str(note_id),
                 self.XML_CREATION_TAG : creation,
                 self.XML_LASTMODIFY_TAG : modify,
                 self.XML_LINKLIST_TAG : linkList }
                    
        pelem = xml.addChild(self.XML_NOTE_TAG, text, parent, attr)
        if (self.iter_n_children(piter) != 0):
            self.insertXMLEntry(self.iter_children(piter), xml, pelem)
        piter = self.iter_next(piter)
        if (piter != None):
            self.insertXMLEntry(piter, xml, parent)

    # Load
    def insertNoteEntry(self, node, xmlNode):
        # Recursive function to inser a note using the data coming from the XML node
        # node is the node of the xml from where to get data (None = root)
        # xml is the xml object to get data from
        # This function get text and attribute data from XML and add the note element, then
        # it re iterate for each child of node, then
        # it re iterate for each item next (brother) of node
            
        pelem = node
        
        if (xmlNode.tag == self.XML_NOTE_TAG):
            
        
            textbuffer = self.CreateNewBuffer('', self.tagTable, False); # Do not connect "changed" signal
        
            #Text
            if (self.xml_save_mode == self.XML_GTK_SERIALIZE):
                data = xmlNode.text
                textbuffer.begin_not_undoable_action() # Deserialization on load can't be undone
                TextBuffer2HTMLConvert.deserialize(textbuffer, data)
                textbuffer.end_not_undoable_action()
                textbuffer.connect("changed", self.TextChanged) # Connect "changed" signal after de-serialization
            else:
                return
        
            #Attributes
            attr = xmlNode.attrib
            title = attr[self.XML_TITLE_TAG] 
            note_id = int(attr[self.XML_ID_TAG])
            creation = attr[self.XML_CREATION_TAG]
            modify = attr[self.XML_LASTMODIFY_TAG]
            linkList = attr[self.XML_LINKLIST_TAG]
                    
            pelem = self.addNote(node, title, note_id, creation, modify, textbuffer, linkList)
            
        for xmlChild in xmlNode:
            self.insertNoteEntry(pelem, xmlChild)

gobject.type_register(NoteModel)
gobject.signal_new("modified_title", NoteModel, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
gobject.signal_new("modified_text",  NoteModel, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
        
if __name__ == '__main__':
    note = NoteModel()
    note.populate()
    note.CreateNewNote()
    note.save("test.xml")
    pass