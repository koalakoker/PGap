'''
Created on 30/mag/2015

@author: koala
'''

import pygtk
pygtk.require('2.0')
import gtk
import gobject
import datetime

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
                   }
        self.builder.connect_signals(handlers)

        # create a TreeStore with one string column to use as the model
        self.NoteStore = NoteModel()
        #Populate
        self.NoteStore.populate()

        # create the TreeView using NoteStore
        self.treeview =  self.builder.get_object("treeview")
        self.treeview.set_model(self.NoteStore)
        
        columnInfo = ('Note title', 'ID', 'Creation Time', 'Last modify')
        
        self.tvcolumn = [None , None, None, None]
        self.cell = [None , None, None, None]
        
        for i in range(4):
            # create the TreeViewColumn to display the data
            self.tvcolumn[i] = gtk.TreeViewColumn(columnInfo[i])
            # add tvcolumn to treeview
            self.treeview.append_column(self.tvcolumn[i])
            # create a CellRendererText to render the data
            self.cell[i] = gtk.CellRendererText()
            # add the cell to the tvcolumn and allow it to expand
            self.tvcolumn[i].pack_start(self.cell[i], True)
            # set the cell "text" attribute to column 0 - retrieve text
            # from that column in NoteStore
            self.tvcolumn[i].add_attribute(self.cell[i], 'text', i)
            # Allow sorting on the column
            self.tvcolumn[i].set_sort_column_id(i)
            # Allow resize of column
            self.tvcolumn[i].set_resizable(True)
        
        # make it searchable
        self.treeview.set_search_column(0)
        
        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        
    def column(self, column, show):
        self.tvcolumn[column].set_visible(show)
        
    def onTestClk(self, button):
        self.column(0, False)
    
if __name__ == '__main__':
    main = PGapMain()
    gtk.main()
