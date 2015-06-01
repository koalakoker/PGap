'''
Created on 30/mag/2015

@author: koala
'''

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import datetime
import pango

class NoteModel(gtk.TreeStore):
    newPageID = 2 #default value 1 is the welcome screen
    
    def __init__(self):
        gtk.TreeStore.__init__(self, gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        #init treestore with the following types
        # 0: String - Title of the note
        # 1: Int - ID of the note (unique ID inside the db)
        # 2: String - Time stamp (Creation)
        # 3: String - Time stamp (Last modification) 
        # 4: String - Testo nota
        
    def populate(self):
        for parent in range(4):
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            piter = self.append(None, ('parent %i' % parent, self.newPageID, now, now, ""))
            self.newPageID += 1
            for child in range(3):
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                self.append(piter, ('child %i of parent %i' % (child, parent), self.newPageID, now, now, ""))
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
    def delete_event(self, widget, event, data=None):
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
                     "on_Creation Time_toggled": self.updateColumnView
                   }
        self.builder.connect_signals(handlers)

        # create a TreeStore with one string showColumn to use as the model
        self.NoteStore = NoteModel()
        #Populate
        self.NoteStore.populate()

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
        
        self.textbuffer = self.builder.get_object("textbuffer")
        self.tag_bold = self.textbuffer.create_tag("bold",
            weight=pango.WEIGHT_BOLD)
        self.tag_italic = self.textbuffer.create_tag("italic",
            style=pango.STYLE_ITALIC)
        self.tag_underline = self.textbuffer.create_tag("underline",
            underline=pango.UNDERLINE_SINGLE)
        self.tag_found = self.textbuffer.create_tag("found",
            background="yellow")
        
        # to make it nice we'll put the toolbar into the handle box, 
        # so that it can be detached from the main window
        handlebox = gtk.HandleBox()
        self.vbox = self.builder.get_object("vbox")
        self.vbox.pack_start(handlebox, False, False, 0)
        self.vbox.reorder_child(handlebox,0)

        # toolbar will be horizontal, with both icons and text, and
        # with 5pxl spaces between items and finally, 
        # we'll also put it into our handlebox
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar.set_border_width(0)
        handlebox.add(toolbar)

        iconw = gtk.Image()
        iconw.set_from_file("img/bold.png")
        button_bold = toolbar.append_item(
            "Bold",           # button label
            "Bold", # this button's tooltip
            "Private",         # tooltip private info
            iconw,             # icon widget
            self.onTestClk)    # a signal
        
        iconw2 = gtk.Image()
        iconw2.set_from_file("img/underline.png")
        button_undeline = toolbar.append_item(
            "Undeline",           # button label
            "Undeline", # this button's tooltip
            "Private",         # tooltip private info
            iconw2,             # icon widget
            self.onTestClk)    # a signal
        
        iconw3 = gtk.Image()
        iconw3.set_from_file("img/italic.png")
        button_undeline = toolbar.append_item(
            "Italic",           # button label
            "Italic", # this button's tooltip
            "Private",         # tooltip private info
            iconw3,             # icon widget
            self.onTestClk)    # a signal
        
        toolbar.append_space() # space after item
        
        # that's it ! let's show everything.
        toolbar.show()
        handlebox.show()
                
    def updateColumnView(self, CheckMenuItem):
        for i in range(len(self.columnInfo)):
            itm = self.builder.get_object(self.columnInfo[i])
            if (itm != None):
                self.tvcolumn[i].set_visible(itm.get_active())
            
    def onTestClk(self, button):
        self.on_button_clicked(self.tag_bold)
    
    def on_button_clicked(self, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.apply_tag(tag, start, end)
    
if __name__ == '__main__':
    main = PGapMain()
    gtk.main()
