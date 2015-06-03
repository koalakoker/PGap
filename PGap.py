'''
Created on 30/mag/2015

@author: koala
'''

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import gobject
import datetime
import pango
from undobufferrich import undobufferrich
import TextBuffer2HTMLConvert

initText = """Welcome to OGapp!

OGapp is a slim sized and fast program to manage your textual notes. Notes are organized in pages and it is possible to setup a main password to get the access to the notes. When the notes are password protected the .ogp file in which the notes are stored will be encrypted.
OGapp is cross platform and is available for Windows, Linux and (maybe in the future) Mac. It is based on Qt4 and is written in C++.

This software is OPEN SOURCE and released under GPL license so you can feel FREE to use, copy, share, (but above all) to study, analyze and modify it as you like (within the terms of the license).
If you like, hate or simply use this software, if you find any bug or have any request, please do not hesitate to let me know through the services offered by the site that hosts the project or through my Facebook page (http://facebook.com/koalakoker ). And (if you think it's the case) do not hesitate to recommend the program to your friends."""

class NoteModel(gtk.TreeStore):
    newPageID = 2 #default value 1 is the welcome screen
    
    def __init__(self):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gtk.TextBuffer)
        #init treestore with the following types
        # 0: String - Title of the note
        # 1: Int - ID of the note (unique ID inside the db)
        # 2: String - Time stamp (Creation)
        # 3: String - Time stamp (Last modification) 
        # 4: String - Testo nota
        
    def populate(self):
        for parent in range(4):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            it = ""
            if (parent == 0):
                it = initText
            piter = self.append(None, ('parent %i' % parent, self.newPageID, now, now, undobufferrich(it)))
            self.newPageID += 1
            for child in range(3):
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                self.append(piter, ('child %i of parent %i' % (child, parent), self.newPageID, now, now, undobufferrich("")))
                self.newPageID += 1

class PGapMain:
    
    columnInfo = ('Note title', 'ID', 'Creation Time', 'Last Modify')
    
    def getColumnInfo(self, istr):
        #returns the first showColumn that match istr inside columnInfo
        i = 0
        pos = -1
        for s in self.columnInfo:
            if (s == istr):
                if (pos == -1):
                    pos = i
            i += 1
        return pos

    # close the window and quit
    def delete_event(self, widget=None, event=None, data=None):
        gtk.main_quit()
        return False
    
    def __init__(self):
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.window = self.builder.get_object("pgapui")
        self.window.resize(1024,600)
        self.window.show_all()
        self.window.connect("delete_event", self.delete_event)
        
        handlers = { "onDeleteWindow": gtk.main_quit,
                     "onNewButton": self.onTestClk,
                     "onDeleteButton": self.onTestClk,
                     "onTestClk": self.onTestClk,
                     "on_ID_toggled": self.updateColumnView,
                     "on_Last modify_toggled": self.updateColumnView,
                     "on_Creation Time_toggled": self.updateColumnView,
                     "keypress": self.onKeyPress,
                     "keyrelease": self.onKeyRelease,
                     "onCursorChanged": self.onNoteSelectionChange
                   }
        self.builder.connect_signals(handlers)

        # create a TreeStore with one string showColumn to use as the model
        self.NoteStore = NoteModel()
        #Populate
        #self.NoteStore.populate()

        # create the TreeView using NoteStore
        self.treeview =  self.builder.get_object("treeview")
        self.treeview.set_model(self.NoteStore)
        
        self.tvcolumn = []
        self.cell = []
        
        for i in range(len(self.columnInfo)):
            # create the TreeViewColumn to display the data
            self.tvcolumn.append(gtk.TreeViewColumn(self.columnInfo[i]))
            # add tvcolumn to treeview
            self.treeview.append_column(self.tvcolumn[i])
            # create a CellRendererText to render the data
            self.cell.append(gtk.CellRendererText())
            # add the cell to the tvcolumn and allow it to expand
            self.tvcolumn[i].pack_start(self.cell[i], True)
            # set the cell "text" attribute to showColumn 0 - retrieve text
            # from that showColumn in NoteStore
            self.tvcolumn[i].add_attribute(self.cell[i], 'text', i)
            # Allow sorting on the showColumn
            self.tvcolumn[i].set_sort_column_id(i)
            # Allow resize of showColumn
            self.tvcolumn[i].set_resizable(True)
        
        # make it searchable
        self.treeview.set_search_column(0)
        
        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        
        #update column view accordind glade file
        self.updateColumnView(None)
        
        self.textview = self.builder.get_object("textview")
        self.onNoteSelectionChange(self.treeview)
        
        # to make it nice we'll put the toolbar into the handle box, 
        # so that it can be detached from the main window
        handlebox = gtk.HandleBox()
        self.vbox = self.builder.get_object("vbox")
        self.vbox.pack_start(handlebox, False, False, 0)
        self.vbox.reorder_child(handlebox,0)

        # toolbar will be horizontal, with icons and finally, 
        # we'll also put it into our handlebox
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_border_width(0)
        handlebox.add(toolbar)

        iconw = []
        iconw.append(gtk.Image())
        iconw[0].set_from_file("img/bold.png")
        self.tag_bold = self.textbuffer.create_tag("Bold",
            weight=pango.WEIGHT_BOLD)
        toolbar.append_item(
            "Bold",                 # button label
            "Bold",                 # this button's tooltip
            "Private",              # tooltip private info
            iconw[0],               # icon widget
            self.on_BIU_button_clicked, # a signal
            self.tag_bold)          # tag bold
        
        
        iconw.append(gtk.Image())
        iconw[1].set_from_file("img/underline.png")
        self.tag_underline = self.textbuffer.create_tag("Underline",
            underline=pango.UNDERLINE_SINGLE)
        toolbar.append_item(
            "Underline",            # button label
            "Underline",            # this button's tooltip
            "Private",              # tooltip private info
            iconw[1],               # icon widget
            self.on_BIU_button_clicked, # a signal
            self.tag_underline)     # tag underline
        
        iconw.append(gtk.Image())
        iconw[2].set_from_file("img/italic.png")
        self.tag_italic = self.textbuffer.create_tag("Italic",
            style=pango.STYLE_ITALIC)
        toolbar.append_item(
            "Italic",               # button label
            "Italic",               # this button's tooltip
            "Private",              # tooltip private info
            iconw[2],               # icon widget
            self.on_BIU_button_clicked, # a signal
            self.tag_italic)        # tag italic
        
        self.tag_found = self.textbuffer.create_tag("Found",
            background="yellow")
        
        toolbar.append_space() # space after item
        
        # that's it ! let's show everything.
        toolbar.show()
        handlebox.show()
        
        self.keyCtrlPressed = False
                
    def updateColumnView(self, CheckMenuItem):
        for i in range(len(self.columnInfo)):
            itm = self.builder.get_object(self.columnInfo[i])
            if (itm != None):
                self.tvcolumn[i].set_visible(itm.get_active())
                
    def on_BIU_button_clicked(self, button, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.toggleTag(tag, start, end)
    
    def onKeyEsc(self):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            tb = self.textbuffer
            tb.select_range(tb.get_end_iter(),tb.get_end_iter())
        else:
            self.delete_event()
    
    def onKeyRelease(self, widget, event):
        keyPressName = gdk.keyval_name(event.keyval)
        
        if ((keyPressName == "Control_L") or (keyPressName == "Control_R")):
            self.keyCtrlPressed = False
    
    def onKeyPress(self, widget, event):
        keyPressName = gdk.keyval_name(event.keyval)
        
        if (self.keyCtrlPressed):
            if (keyPressName == "b"):
                self.on_BIU_button_clicked(None, self.tag_bold)
            if (keyPressName == "i"):
                self.on_BIU_button_clicked(None, self.tag_italic)
            if (keyPressName == "u"):
                self.on_BIU_button_clicked(None, self.tag_underline)
            if (keyPressName == "z"):
                self.textbuffer.undo()
            if ((keyPressName == "y") or (keyPressName == "Z")):
                self.textbuffer.redo()
        
        if ((keyPressName == "Control_L") or (keyPressName == "Control_R")):
            self.keyCtrlPressed = True
            
        if (keyPressName == "Escape"):
            self.onKeyEsc()
#         print (gtk.gdk.keyval_name(event.keyval))

    def onNoteSelectionChange(self, treeView):
        itersel = treeView.get_selection().get_selected()[1]
        if (itersel == None):
            itersel = self.NoteStore.get_iter_root()
        if (itersel != None):
            self.textbuffer = self.NoteStore.get_value(itersel, 4) # Mergiare con l'on-change
            self.textview.set_buffer(self.textbuffer)
    
    def onTestClk(self, button):
#         TextBuffer2HTMLConvert.toHTML(self.textbuffer)
#         TextBuffer2HTMLConvert.serialize(self.textbuffer)
        diag = gtk.MessageDialog()
        diag.show()
    
if __name__ == '__main__':
    main = PGapMain()
    gtk.main()
